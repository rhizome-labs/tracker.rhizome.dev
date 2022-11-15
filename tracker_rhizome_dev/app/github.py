from datetime import datetime
from tracemalloc import start
from typing import Union
from urllib.parse import parse_qs, urlparse

from requests.exceptions import HTTPError
from tracker_rhizome_dev import ENV
from tracker_rhizome_dev.app.http_request import HttpReq


class Github:
    def __init__(self) -> None:
        self.github_api_url = "https://api.github.com"
        self.headers = {"Authorization": f"Bearer {ENV['GITHUB_API_KEY']}"}

    async def get_org(self, org_name: str) -> Union[dict, None]:
        """
        Returns a dictionary containing details about a GitHub organization.
        """
        url = f"{self.github_api_url}/orgs/{org_name}"
        r = await HttpReq.get(url, headers=self.headers)
        data = r.json()
        return data

    async def get_repos_from_username(
        self, username: str, page: int = 1
    ) -> Union[list, None]:
        """
        Returns a list of repositories for a GitHub user.
        """
        try:
            url = (
                f"{self.github_api_url}/users/{username}/repos?page={page}&per_page=100"
            )
            r = await HttpReq.get(url, headers=self.headers)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    return data
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(e)
            return None

    async def get_commit_details(self, owner_name: str, repo_name: str, hash: str):
        """
        Returns the metadata for a GitHub commit.
        """
        try:
            url = f"{self.github_api_url}/repos/{owner_name}/{repo_name}/commits/{hash}"
            r = await HttpReq.get(url, headers=self.headers)
            if r.status_code == 200:
                data = r.json()
                return data
            else:
                return None
        except Exception as e:
            print(e)
            return None

    async def get_commits(
        self,
        owner_name: str,
        repo_name: str,
        start_timestamp: int = None,
        end_timestamp: int = None,
        page: int = 1,
    ) -> Union[list, None]:
        """
        Returns a list of commits for a GitHub repository.
        """

        # Create query string for start timestamp
        if start_timestamp is not None:
            start_dt = (
                datetime.utcfromtimestamp(start_timestamp)
                .replace(microsecond=0)
                .isoformat()
            )
            start_timestamp_str = f"&since={start_dt}"
        else:
            start_timestamp_str = ""

        # Create query string for end timestamp
        if end_timestamp is not None:
            end_dt = (
                datetime.utcfromtimestamp(end_timestamp)
                .replace(microsecond=0)
                .isoformat()
            )
            end_timestamp_str = f"&until={end_dt}"
        else:
            end_timestamp_str = ""

        try:
            url = f"{self.github_api_url}/repos/{owner_name}/{repo_name}/commits?page={page}&per_page=100{self._generate_timestamp_query_string(start_timestamp, end_timestamp)}"
            r = await HttpReq.get(url, headers=self.headers)
            data = r.json()
            if r.status_code == 200:
                if len(data) > 0:
                    return data
                else:
                    return None
            else:
                return None
        except:
            return None

    async def get_commits_count(
        self,
        owner_name: str,
        repo_name: str,
        start_timestamp: int = None,
        end_timestamp: int = None,
    ) -> int:
        """
        Returns the number of commits for a GitHub repository.
        """
        url = f"{self.github_api_url}/repos/{owner_name}/{repo_name}/commits?per_page=1{self._generate_timestamp_query_string(start_timestamp, end_timestamp)}"
        r = await HttpReq.get(url, headers=self.headers)
        links = r.links
        try:
            rel_last_link_url = urlparse(links["last"]["url"])
            rel_last_link_url_args = parse_qs(rel_last_link_url.query)
            rel_last_link_url_page_arg = rel_last_link_url_args["page"][0]
            commits_count = int(rel_last_link_url_page_arg)
            return commits_count
        except KeyError:
            return 0

    async def get_releases(
        self, owner_name: str, repo_name: str, page: int = 1
    ) -> Union[list, None]:
        """
        Returns a list of releases for a GitHub repository.
        """
        url = f"{self.github_api_url}/repos/{owner_name}/{repo_name}/releases?page={page}&per_page=100"
        r = await HttpReq.get(url, headers=self.headers)
        data = r.json()
        if len(data) > 0:
            return data
        else:
            return None

    def _generate_timestamp_query_string(
        self, start_timestamp: int, end_timestamp: int
    ) -> str:
        # Create query string for start timestamp
        if start_timestamp is not None:
            start_dt = (
                datetime.utcfromtimestamp(start_timestamp)
                .replace(microsecond=0)
                .isoformat()
            )
            start_timestamp_str = f"&since={start_dt}"
        else:
            start_timestamp_str = ""

        # Create query string for end timestamp
        if end_timestamp is not None:
            end_dt = (
                datetime.utcfromtimestamp(end_timestamp)
                .replace(microsecond=0)
                .isoformat()
            )
            end_timestamp_str = f"&until={end_dt}"
        else:
            end_timestamp_str = ""

        return f"{start_timestamp_str}{end_timestamp_str}"
