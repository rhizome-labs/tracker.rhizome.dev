###########################################################
# ██████╗ ██╗  ██╗██╗███████╗ ██████╗ ███╗   ███╗███████╗ #
# ██╔══██╗██║  ██║██║╚══███╔╝██╔═══██╗████╗ ████║██╔════╝ #
# ██████╔╝███████║██║  ███╔╝ ██║   ██║██╔████╔██║█████╗   #
# ██╔══██╗██╔══██║██║ ███╔╝  ██║   ██║██║╚██╔╝██║██╔══╝   #
# ██║  ██║██║  ██║██║███████╗╚██████╔╝██║ ╚═╝ ██║███████╗ #
# ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝ #
###########################################################

__version__ = "0.1.0"

import builtins
import os
from functools import lru_cache

import rich
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

# Override standard print library
builtins.print = rich.print

# Load environment variables
@lru_cache(maxsize=1)
def env():
    load_dotenv()
    return {
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_URL": os.getenv("DB_URL"),
        "DISCORD_WEBHOOK_URL": os.getenv("DISCORD_WEBHOOK_URL"),
        "ENV": os.getenv("ENV"),
        "GITHUB_API_KEY": os.getenv("GITHUB_API_KEY"),
        "ICON_API_ENDPOINT": os.getenv("ICON_API_ENDPOINT"),
        "ICON_TRACKER_ENDPOINT": os.getenv("ICON_TRACKER_ENDPOINT"),
    }


ENV = env()

# Set max workers based on CPU count
MAX_WORKERS = int(os.cpu_count() * 4)

# Set Redis caching expiration times
if ENV["ENV"] == "PRODUCTION":
    CACHE_30S = 30
    CACHE_60S = 60
else:
    CACHE_30S = 1
    CACHE_60S = 1

# Set ICX gensis timestamp
GENESIS_TIMESTAMP_S = 1516819217

# Set loop decimal count
EXA = 10**18

# Set tracked GitHub usernames
@lru_cache(maxsize=1)
def get_github_usernames():
    GITHUB_USERNAMES = [
        "balancednetwork",
        "espanicon",
        "icon-community",
        "icon-project",
        "openmoneymarket",
        "rhizome-labs",
        "staky-io",
        "sudoblockio",
    ]
    return sorted(GITHUB_USERNAMES, key=lambda v: v.casefold())


# Additional repos to track
GITHUB_ADDITIONAL_REPOS = [("web3labs", "ice-substrate")]

GITHUB_USERNAMES = get_github_usernames()

# Set ignored repos
GITHUB_IGNORED_REPO_IDS = [
    419481604,
    131121676,
    125140421,
    356387774,
    422671636,
    358748490,
    419252594,
    346519273,
    347179227,
    462903782,
    326794018,
    346642799,
    434479312,
    347181119,
    347181250,
    347176745,
    347177139,
    368600737,
    347176870,
    347175004,
    347176204,
    347176432,
]

# Load Jinja2 templates
@lru_cache(maxsize=1)
def load_templates():
    return Jinja2Templates(directory=f"{os.path.dirname(__file__)}/app/templates")


TEMPLATES = load_templates()
