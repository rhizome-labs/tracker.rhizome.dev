import json
from datetime import datetime
from decimal import Decimal
from typing import List, Union

import pymongo
from beanie import Document, Indexed
from pydantic import BaseModel, root_validator, validator
from tracker_rhizome_dev import EXA
from tracker_rhizome_dev.app.data.country_codes import CountryCodes
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.utils import format_number, format_percentage, to_int


class Db_GithubCommit(Document):
    id: str  # SHA Hash
    date: datetime
    owner_name: Indexed(str)
    repo_id: Indexed(int)
    repo_name: Indexed(str)
    author_email: str
    author_id: int = 0
    author_name: str
    author_username: Union[str, None]
    committer_email: str
    committer_id: int = 0
    committer_name: str
    committer_username: Union[str, None]
    message: Indexed(str)
    changes_additions: int
    changes_deletions: int
    changes_total: int

    @validator("date")
    def validate_datetime(cls, v: datetime):
        return v.replace(tzinfo=None)

    class Settings:
        name = "githubCommits"


# githubReleases


class Db_GithubReleases(Document):
    id: str

    class Settings:
        name = "githubReleases"


# githubRepos


class Db_GithubRepo(Document):
    id: int
    name: Indexed(str)
    description: Union[str, None]
    owner_name: Indexed(str)
    language: Union[str, None]
    license: Union[str, None]
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    total_commits: int = 0

    @validator("created_at", "pushed_at", "updated_at")
    def validate_datetime(cls, v: datetime):
        return v.replace(tzinfo=None)

    @validator("owner_name")
    def validate_owner_name(cls, v: str):
        return v.lower()

    class Settings:
        name = "githubRepos"


class Db_GithubRepoOwnerNameView(BaseModel):
    owner_name: str


# icxSicxBnusdQuotes


class Db_IcxSicxBnusdQuote(Document):
    id: datetime
    icx_usd: Decimal
    sicx_bnusd: Decimal
    sicx_icx: Decimal

    class Settings:
        name = "icxSicxBnusdQuotes"
