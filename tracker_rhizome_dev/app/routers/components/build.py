import calendar
import json
from datetime import datetime, timedelta
from itertools import groupby

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from tracker_rhizome_dev import (
    ENV,
    GITHUB_IGNORED_REPO_IDS,
    GITHUB_USERNAMES,
    TEMPLATES,
)
from tracker_rhizome_dev.app.http_request import HttpReq
from tracker_rhizome_dev.app.models.github import Db_GithubCommit, Db_GithubRepo
from tracker_rhizome_dev.app.utils import format_number, format_percentage

router = APIRouter(prefix="/build")


@router.get("/commits/leaderboard/")
async def get_commit_leaderboard(request: Request):
    committers = await Db_GithubCommit.distinct(Db_GithubCommit.author_id)
    return TEMPLATES.TemplateResponse(
        "build/components/leaderboard.html",
        {
            "request": request,
            "committers": committers,
        },
    )


@router.get("/commits/")
async def get_commits(request: Request):
    # Get datetime object for current utc time
    dt_now = datetime.utcnow().replace(microsecond=0)
    dt_30d_ago = dt_now - timedelta(days=30)
    dt_now_timestamp = int(dt_now.timestamp())
    dt_30d_ago_timestamp = int(dt_30d_ago.timestamp())

    commits = (
        await Db_GithubCommit.find(
            Db_GithubCommit.date >= dt_30d_ago,
            Db_GithubCommit.date <= dt_now,
        )
        .sort(-Db_GithubCommit.date)
        .to_list()
    )

    commits = [
        commit for commit in commits if commit.repo_id not in GITHUB_IGNORED_REPO_IDS
    ]

    return TEMPLATES.TemplateResponse(
        "build/components/commits.html",
        {
            "request": request,
            "commits": commits,
            "start_timestamp": dt_30d_ago_timestamp,
            "end_timestamp": dt_now_timestamp,
        },
    )


@router.get("/commits-7d-chart/")
async def get_commits_week_chart(request: Request):
    now = datetime.utcnow().replace(microsecond=0)
    start_dt = now - timedelta(days=7)
    end_dt = now

    commits = (
        await Db_GithubCommit.find(
            Db_GithubCommit.date >= start_dt,
            Db_GithubCommit.date <= end_dt,
        )
        .sort(+Db_GithubCommit.date)
        .to_list()
    )

    commits_datapoints = []
    for k, v in groupby(commits, key=lambda x: x.date.strftime("%Y-%m-%dT%H")):
        commits_datapoints.append({"x": k, "y": len(list(v))})

    return TEMPLATES.TemplateResponse(
        "build/components/commits_7d_chart.html",
        {
            "request": request,
            "chart_id": "commits",
            "data": commits_datapoints,
            "total_commits": format_number(len(commits)),
        },
    )


@router.get("/commits-ytd-chart/")
async def get_commits_ytd_chart(request: Request):
    now = datetime.utcnow().replace(microsecond=0)
    start_dt = datetime(now.year, 1, 1, 0, 0)
    end_dt = datetime(now.year, 12, 31, 23, 59)

    commits = (
        await Db_GithubCommit.find(
            Db_GithubCommit.date >= start_dt,
            Db_GithubCommit.date <= end_dt,
        )
        .sort(+Db_GithubCommit.date)
        .to_list()
    )

    commits_datapoints = []
    for k, v in groupby(commits, key=lambda x: x.date.strftime("%Y-%m")):
        print(k)
        commits_datapoints.append({"x": k, "y": len(list(v))})

    return TEMPLATES.TemplateResponse(
        "build/components/commits_ytd_chart.html",
        {
            "request": request,
            "chart_id": "commits",
            "data": commits_datapoints,
            "total_commits": format_number(len(commits)),
        },
    )


@router.get("/owners/")
async def get_owners(request: Request):
    url = f'{ENV["API_URL"]}/build/owners/'
    r = await HttpReq.get(url)
    data = r.json()["data"]
    return TEMPLATES.TemplateResponse(
        "build/components/owners.html",
        {"request": request, "data": data},
    )


@router.get("/repos/")
async def get_repos(request: Request, owner_name: str = Query(default=None)):
    if owner_name is not None:
        # Raise error if owner_name is not in tracked usernames
        if owner_name.lower() not in GITHUB_USERNAMES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Sorry, {owner_name} could not be found. Valid owner names are {', '.join(GITHUB_USERNAMES)}.",
            )
        # If owner name is valid, query database for repos belonging to that user
        else:
            repos = await Db_GithubRepo.find(
                Db_GithubRepo.owner_name == owner_name.lower()
            ).to_list()
    # If owner_name is None, query for all repos
    else:
        repos = await Db_GithubRepo.find_all().to_list()

    # Sort repos by name
    repos.sort(key=lambda x: x.name.casefold())

    repos = [repo for repo in repos if repo.id not in GITHUB_IGNORED_REPO_IDS]

    return TEMPLATES.TemplateResponse(
        "build/components/repos.html",
        {
            "request": request,
            "owners": GITHUB_USERNAMES,
            "repos": repos,
        },
    )
