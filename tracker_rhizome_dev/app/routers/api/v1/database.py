import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, status
from pymongo.errors import BulkWriteError, DuplicateKeyError
from rich import inspect

from tracker_rhizome_dev import (
    GENESIS_TIMESTAMP_S,
    GITHUB_IGNORED_REPO_IDS,
    GITHUB_USERNAMES,
    MAX_WORKERS,
)
from tracker_rhizome_dev.app.balanced import Balanced
from tracker_rhizome_dev.app.github import Github
from tracker_rhizome_dev.app.gov import Gov
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.models.balanced import (
    Db_BalancedLoan,
    Db_BalancedPoolDynamicDataSnapshot,
    Db_BalancedPoolStaticData,
)
from tracker_rhizome_dev.app.models.github import (
    Db_GithubCommit,
    Db_GithubReleases,
    Db_GithubRepo,
)
from tracker_rhizome_dev.app.models.icx import (
    Db_IcxBlock,
    Db_IcxSicxBnusdQuote,
    Db_RecentBlock,
    Db_RecentTransaction,
    Db_ValidatorNodeStatus,
)
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import (
    get_datetime_in_utc,
    send_discord_notification,
    to_int,
)

router = APIRouter(prefix="/database")


@router.post("/balanced/loans/", status_code=status.HTTP_201_CREATED)
async def post_balanced_loans():
    balanced = Balanced()

    loans = balanced.get_loans(dump=False)
    loans = [Db_BalancedLoan(id=loan.pos_id, **dict(loan)) for loan in loans]

    existing_loans = await Db_BalancedLoan.find_all().to_list()
    existing_loan_ids = [loan.id for loan in existing_loans]

    loans_to_write = [loan for loan in loans if loan.id not in existing_loan_ids]
    loans_to_replace = [loan for loan in loans if loan.id in existing_loan_ids]

    if len(loans_to_write) > 0:
        await Db_BalancedLoan.insert_many(loans_to_write)

    if len(loans_to_replace) > 0:
        await Db_BalancedLoan.replace_many(loans_to_replace)

    return


@router.post("/recent-blocks/", status_code=status.HTTP_201_CREATED)
async def post_recent_blocks(limit: int = 50):
    # Fetch recent blocks from Tracker API.
    blocks = await Tracker.get_blocks(limit=limit, format=False)
    recent_blocks = [Db_RecentBlock(id=block["number"], **block) for block in blocks]

    # Get blocks that are currently in the database.
    existing_blocks = await Db_RecentBlock.find_all().to_list()
    print(f"There are {len(existing_blocks)} in the database.")

    # Create a list of block heights. Set to None if there are no blocks in the database.
    if len(existing_blocks) >= 0:
        existing_block_heights = [block.id for block in existing_blocks]
        blocks_to_write = [
            block for block in recent_blocks if block.id not in existing_block_heights
        ]
    else:
        existing_block_heights = None
        blocks_to_write = recent_blocks

    print(f"Writing {len(blocks_to_write)} blocks to the database...")
    db_write = await Db_RecentBlock.insert_many(blocks_to_write)

    return


@router.post("/recent-transactions/", status_code=status.HTTP_201_CREATED)
async def post_recent_transactions(limit: int = 50):
    transactions = await Tracker.get_transactions(limit=limit, format=False)
    recent_transactions = [
        Db_RecentTransaction(id=tx["hash"], **tx) for tx in transactions
    ]
    return recent_transactions


@router.post(
    "/balanced/pool-static-data-snapshot/", status_code=status.HTTP_201_CREATED
)
async def insert_balanced_pool_static_data_snapshot():
    balanced = Balanced()
    # Get current static data from the blockchain.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(balanced.get_pool_static_metadata, pool_id=id)
            for id in range(1, balanced.get_pool_count())
        ]
        static_data = [future.result() for future in futures]
        static_data.sort(key=lambda k: k.id)

    # Write static data to database.
    for record in static_data:
        db_write = await record.save()
        print(db_write)

    return


@router.post(
    "/balanced/pool-dynamic-data-snapshot/", status_code=status.HTTP_201_CREATED
)
async def insert_balanced_pool_dynamic_data_snapshot(
    timestamp: int = Query(default=None, ge=GENESIS_TIMESTAMP_S)
):
    """
    Inserts Balanced pool dynamic data into a MongoDB collection.

    Args:
        timestamp (int): Unix timestamp in seconds (must be greater than 1516819217)

    Returns:
        A dictionary of the inserted document.
    """
    balanced = Balanced()

    # Set block height for the given timestamp. Set to latest block height if timestamp is 'None'.
    if timestamp is not None:
        block_height = await Tracker.get_block_from_timestamp(timestamp)
    else:
        block_height = Icx.get_block()["height"]

    print(f"Fetching Balanced pool dynamic data at block {block_height}...")

    pool_count = balanced.get_pool_count(height=block_height)

    print(f"There were {pool_count} pools at block {block_height}...")

    # Get dynamic data from the blockchain.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                balanced.get_pool_dynamic_metadata, pool_id=id, height=block_height
            )
            for id in range(1, pool_count + 1)
        ]
        dynamic_data = [
            future.result() for future in futures if future.result() is not None
        ]
        dynamic_data.sort(key=lambda k: k.id)
    print(get_datetime_in_utc(timestamp))
    # Write dynamic data to database.
    db_write = Db_BalancedPoolDynamicDataSnapshot(
        id=get_datetime_in_utc(timestamp), data=dynamic_data
    )
    try:
        await db_write.insert()
    except DuplicateKeyError:
        await db_write.replace()
    return


@router.post("/insert/icx-sicx-bnusd-quotes/", status_code=status.HTTP_201_CREATED)
async def insert_icx_sicx_bnusd_quotes():
    balanced = Balanced()
    icx_usd_price = Decimal(balanced.get_icx_usd_price())
    sicx_bnusd_price = Decimal(
        to_int(balanced.get_price_by_name("sICX/bnUSD"))
    ) / Decimal(10**18)
    sicx_icx_price = Decimal(to_int(balanced.get_price_by_name("sICX/ICX"))) / Decimal(
        10**18
    )
    db_write = Db_IcxSicxBnusdQuote(
        id=get_datetime_in_utc(),
        icx_usd=icx_usd_price,
        sicx_bnusd=sicx_bnusd_price,
        sicx_icx=sicx_icx_price,
    )
    await db_write.insert()
    return


@router.post("/insert/validators-node-status/", status_code=status.HTTP_201_CREATED)
async def insert_validators_node_status():
    validators_node_status = Gov.get_validators_node_status()
    timestamp = get_datetime_in_utc()
    for address, status in validators_node_status.items():
        db_write = Db_ValidatorNodeStatus(
            id=address, timestamp=timestamp, status=status
        )
        await db_write.save()
    return


@router.post("/github/commits2/")
async def insert_github_commits(
    request: Request,
    background_tasks: BackgroundTasks,
    start_timestamp: int = 1640995200,
    end_timestamp: int = None,
):
    """
    Fetches GitHub commits for tracked repositories and inserts them into a MongoDB database.
    """

    # Initialize Github class.
    github = Github()

    # Get current time.
    dt_now = datetime.utcnow().replace(microsecond=0, second=0)

    # Set end timestamp to now if not provided.
    if end_timestamp is None:
        end_timestamp = dt_now.timestamp()

    # Get all repos from the database.
    repos = await Db_GithubRepo.find_all().to_list()

    # Filter out ignored repos
    repos = [repo for repo in repos if repo.id not in GITHUB_IGNORED_REPO_IDS]

    for repo in repos[:1]:

        # Query the database for existing commits in this repo
        commits_in_db = await Db_GithubCommit.find(
            Db_GithubCommit.owner_name == repo.owner_name,
            Db_GithubCommit.repo_name == repo.name,
            Db_GithubCommit.date >= datetime.utcfromtimestamp(start_timestamp),
            Db_GithubCommit.date <= datetime.utcfromtimestamp(end_timestamp),
        ).to_list()

        commits_in_db_count = len(commits_in_db)

        print(f"There are {commits_in_db_count} commits for {repo.name} in the database.")  # fmt: skip

        commits_on_github_count = await github.get_commits_count(
            repo.owner_name,
            repo.name,
            start_timestamp,
            end_timestamp,
        )

        print(f"There are {commits_on_github_count} commits for {repo.name} on GitHub.")  # fmt: skip

        # Process commits if the number of commits on GitHub
        # is not equal to the number of commits in the database
        if commits_in_db_count != commits_on_github_count:

            # Initialize array to hold commits
            commits = []

            print(f"Processing {repo.owner_name}-{repo.name}")

            # Get GitHub commits for current page iteration.
            repo_commits = await github.get_commits(
                owner_name=repo.owner_name,
                repo_name=repo.name,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            )

            # Break out of this repo loop if there are no commits.
            if repo_commits is None:
                break
            else:
                # Loop through repo's commits and do some processing.
                for commit in repo_commits:
                    # Get the commit details for a commit.
                    commit_details = await github.get_commit_details(
                        repo.owner_name, repo.name, commit["sha"]
                    )

                    # Process commit author.
                    if commit_details["author"] is None:
                        author_username = None
                        author_id = 0
                    else:
                        author_username = commit_details["author"]["login"]
                        author_id = commit_details["author"]["id"]

                    # Process commit committer.
                    if commit_details["committer"] is None:
                        committer_username = None
                        committer_id = 0
                    else:
                        committer_username = commit_details["committer"]["login"]  # fmt: skip
                        committer_id = commit_details["author"]["id"]

                print(commit)

    #                        except:
    #                            print(commit)
    #                            commits.append(
    #                                Db_GithubCommit(
    #                                    id=commit_details["sha"],
    #                                    date=commit_details["commit"]["committer"]["date"],
    #                                    owner_name=repo.owner_name,
    #                                    repo_id=repo.id,
    #                                    repo_name=repo.name,
    #                                    author_email=commit_details["commit"]["author"][
    #                                        "email"
    #                                    ],
    #                                    author_id=author_id,
    #                                    author_name=commit_details["commit"]["author"][
    #                                        "name"
    #                                    ],
    #                                    author_username=author_username,
    #                                    committer_email=commit_details["commit"][
    #                                        "committer"
    #                                    ]["email"],
    #                                    committer_id=committer_id,
    #                                    committer_name=commit_details["commit"][
    #                                        "committer"
    #                                    ]["name"],
    #                                    committer_username=committer_username,
    #                                    message=commit_details["commit"]["message"],
    #                                    changes_additions=commit_details["stats"][
    #                                        "additions"
    #                                    ],
    #                                    changes_deletions=commit_details["stats"][
    #                                        "deletions"
    #                                    ],
    #                                    changes_total=commit_details["stats"]["total"],
    #                                )
    #                            )
    #
    #                    print(f"Writing {len(commits)} to database...")
    #                    for commit in commits:
    #                        db_write = await commit.save()
    #                        print(db_write)
    #
    #                    page += 1
    #        else:
    #            print("Commits on GitHub and database are equal. Skipping this repo...")
    #            continue

    return


@router.post("/github/commits/")
async def insert_github_commits(
    request: Request,
    background_tasks: BackgroundTasks,
    start_timestamp: int = None,
    end_timestamp: int = None,
    owner_name: str = None,
):
    """
    Fetches GitHub commits for tracked repositories and inserts them into a MongoDB database.
    """

    dt_now = datetime.utcnow().replace(microsecond=0, second=0)

    if end_timestamp is None:
        end_timestamp = int(dt_now.timestamp())

    async def _run_task(
        request,
        start_timestamp: int = None,
        end_timestamp: int = None,
    ):

        github = Github()

        # Get all repos from the database
        repos = await Db_GithubRepo.find_all().to_list()

        # Filter out ignored repos
        repos = [repo for repo in repos if repo.id not in GITHUB_IGNORED_REPO_IDS]

        if owner_name is not None:
            repos = [repo for repo in repos if repo.owner_name == owner_name]

        # Loop through repos
        print(f"Processing {len(repos)} GitHub repos...")

        for repo in repos:

            if start_timestamp is None:
                most_recent_document = (
                    await Db_GithubCommit.find(Db_GithubCommit.repo_name == repo.name)
                    .sort(-Db_GithubCommit.date)
                    .limit(1)
                    .first_or_none()
                )

                print(most_recent_document)

                start_timestamp = int(most_recent_document.date.timestamp())

                print(f"{start_timestamp}!!!")

            print(f"{start_timestamp}???")

            print(
                f"Processing {repo.name} repo from {datetime.utcfromtimestamp(start_timestamp)} to {datetime.utcfromtimestamp(end_timestamp)}..."
            )

            # Query the database for existing commits in this repo
            commits_in_db = await Db_GithubCommit.find(
                Db_GithubCommit.owner_name == repo.owner_name,
                Db_GithubCommit.repo_name == repo.name,
                Db_GithubCommit.date >= datetime.utcfromtimestamp(start_timestamp),
                Db_GithubCommit.date <= datetime.utcfromtimestamp(end_timestamp),
            ).to_list()

            if commits_in_db is None:
                commits_in_db_count = 0
            else:
                commits_in_db_count = len(commits_in_db)

            print(
                f"There are {commits_in_db_count} commits for {repo.name} in the database."
            )

            commits_on_github_count = await github.get_commits_count(
                repo.owner_name, repo.name, start_timestamp, end_timestamp
            )

            print(
                f"There are {commits_on_github_count} commits for {repo.name} on GitHub."
            )

            # Process commits if the number of commits on GitHub
            # is not equal to the number of commits in the database
            if commits_in_db_count != commits_on_github_count:
                # Initialize array to hold commits
                commits = []
                page = 1
                # Loop through pages and append commits to 'commits' array
                while True:
                    print(f"Processing {repo.owner_name}-{repo.name}: Page {page}")
                    result = await github.get_commits(
                        owner_name=repo.owner_name,
                        repo_name=repo.name,
                        start_timestamp=start_timestamp,
                        end_timestamp=end_timestamp,
                        page=page,
                    )
                    if result is None:
                        break
                    else:
                        for commit in result:

                            try:
                                commit_details = await github.get_commit_details(
                                    repo.owner_name, repo.name, commit["sha"]
                                )

                                if commit_details["author"] is None:
                                    author_username = None
                                    author_id = 0
                                else:
                                    author_username = commit_details["author"]["login"]
                                    author_id = commit_details["author"]["id"]

                                if commit_details["committer"] is None:
                                    committer_username = None
                                    committer_id = 0
                                else:
                                    committer_username = commit_details["committer"][
                                        "login"
                                    ]
                                    committer_id = commit_details["author"]["id"]
                            except:
                                print(commit)

                            commits.append(
                                Db_GithubCommit(
                                    id=commit_details["sha"],
                                    date=commit_details["commit"]["committer"]["date"],
                                    owner_name=repo.owner_name,
                                    repo_id=repo.id,
                                    repo_name=repo.name,
                                    author_email=commit_details["commit"]["author"][
                                        "email"
                                    ],
                                    author_id=author_id,
                                    author_name=commit_details["commit"]["author"][
                                        "name"
                                    ],
                                    author_username=author_username,
                                    committer_email=commit_details["commit"][
                                        "committer"
                                    ]["email"],
                                    committer_id=committer_id,
                                    committer_name=commit_details["commit"][
                                        "committer"
                                    ]["name"],
                                    committer_username=committer_username,
                                    message=commit_details["commit"]["message"],
                                    changes_additions=commit_details["stats"][
                                        "additions"
                                    ],
                                    changes_deletions=commit_details["stats"][
                                        "deletions"
                                    ],
                                    changes_total=commit_details["stats"]["total"],
                                )
                            )

                    print(f"Writing {len(commits)} to database...")
                    for commit in commits:
                        db_write = await commit.save()
                        print(db_write)

                    page += 1
            else:
                print("Commits on GitHub and database are equal. Skipping this repo...")
                continue

        return

    try:
        background_tasks.add_task(_run_task, request, start_timestamp, end_timestamp)
        await send_discord_notification(f"SUCCESS: {request.url}")
    except:
        await send_discord_notification(f"FAIL: {request.url}")

    return


@router.post("/github/repos/", status_code=status.HTTP_201_CREATED)
async def post_github_repos(
    request: Request,
    background_tasks: BackgroundTasks,
    owner_name: str = None,
):

    if owner_name is None:
        owner_names = GITHUB_USERNAMES
    elif owner_name not in GITHUB_USERNAMES:
        owner_names = GITHUB_USERNAMES
    else:
        owner_names = [owner_name]

    async def _run_task(request):
        github = Github()
        repos = []
        for username in owner_names:
            print(f"Processing repos owned by {username}...")
            page = 1
            while True:
                user_repos = await github.get_repos_from_username(username, page=page)
                if user_repos is None:
                    break
                else:
                    for repo in user_repos:
                        if (
                            repo["id"] not in GITHUB_IGNORED_REPO_IDS
                            and repo["fork"] is not True
                        ):
                            print(
                                f'Appending Repo #{repo["id"]} ({repo["name"]}) to repos array...'
                            )
                            repos.append(
                                Db_GithubRepo(
                                    id=repo["id"],
                                    name=repo["name"],
                                    description=repo["description"],
                                    owner_name=repo["owner"]["login"],
                                    language=repo["language"],
                                    created_at=repo["created_at"],
                                    pushed_at=repo["pushed_at"],
                                    updated_at=repo["updated_at"],
                                )
                            )
                page += 1

        # Fetch all repos from database.
        print("Fetching all repos from database.")
        repos_in_db = await Db_GithubRepo.find_all().to_list()

        # Create a dictionary that maps repo ID to repo object.
        repos_in_db_dict = {str(repo.id): repo for repo in repos_in_db}

        for repo in repos:
            try:
                # Check if current repo is in the database.
                repo_in_db = repos_in_db_dict[str(repo.id)]
                # If repo exists in database, compare pushed_at and updated_at dates to see if anything changed.
                # If they're not equal, overwrite database entry.
                if (
                    f"{str(repo.pushed_at)}{str(repo.updated_at)}"
                    != f"{str(repo_in_db.pushed_at)}{str(repo_in_db.updated_at)}"
                ):
                    db_write = await Db_GithubRepo.save(repo)
                    print(db_write)
            # KeyError happens when a repo can't be found in 'repos_in_db_dict'. In that case, save to database.
            except KeyError:
                db_write = await Db_GithubRepo.save(repo)
        return

    try:
        background_tasks.add_task(_run_task, request)
        await send_discord_notification(f"SUCCESS: {request.url}")
    except:
        await send_discord_notification(f"FAIL: {request.url}")

    return


@router.post("/recent-transactions/", status_code=status.HTTP_201_CREATED)
async def post_recent_transactions(request: Request):
    recent_transactions = await Tracker.get_transactions(limit=50)
    recent_transactions = [
        Db_RecentTransaction(id=transaction["hash"], **transaction)
        for transaction in recent_transactions
    ]
    for transaction in recent_transactions:
        db_write = await transaction.save()
    return
