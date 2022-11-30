import json
import os

from beanie import init_beanie
from fastapi import Depends, FastAPI, Form, Path, Query, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.dependencies import is_htmx_request
from tracker_rhizome_dev.app.http_request import HttpReq
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
from tracker_rhizome_dev.app.regex import ICX_ADDRESS_REGEX, ICX_TX_HASH_REGEX

# Import API routes
from tracker_rhizome_dev.app.routers.api.v1 import database as api_database
from tracker_rhizome_dev.app.routers.api.v1 import icx as api_icx

# Import app routes
from tracker_rhizome_dev.app.routers.app import dapps as app_dapps

# Import component routes
from tracker_rhizome_dev.app.routers.components import address, address_book
from tracker_rhizome_dev.app.routers.components import balanced as comp_balanced
from tracker_rhizome_dev.app.routers.components import build as comp_build
from tracker_rhizome_dev.app.routers.components import contracts as comp_contracts
from tracker_rhizome_dev.app.routers.components import governance as comp_governance
from tracker_rhizome_dev.app.routers.components import home as comp_home
from tracker_rhizome_dev.app.routers.components import icx as comp_icx
from tracker_rhizome_dev.app.routers.components import transaction as comp_transaction
from tracker_rhizome_dev.app.routers.components import transactions as comp_transactions
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import format_number

app = FastAPI()

# Mount /static folder
app.mount(
    "/assets",
    StaticFiles(directory=f"{os.path.dirname(__file__)}/static", html=True),
    name="static",
)

# API Routes
app.include_router(api_database.router, prefix="/api/v1", tags=["api"])
app.include_router(api_icx.router, prefix="/api/v1", tags=["api"])

# App Routes
app.include_router(app_dapps.router, tags=["app"])

# Component Routes
app.include_router(
    address.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    address_book.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_balanced.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_build.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_contracts.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_governance.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_home.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_icx.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_transaction.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)
app.include_router(
    comp_transactions.router,
    prefix="/components",
    tags=["components"],
    dependencies=[Depends(is_htmx_request)],
)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    tags=["app"],
)
async def index(request: Request):
    return TEMPLATES.TemplateResponse(
        "home/index.html",
        {
            "request": request,
            "title": "Home",
        },
    )


@app.get(
    "/address/{address}/",
    status_code=status.HTTP_200_OK,
    tags=["app"],
)
async def get_address(
    request: Request,
    address: str = Path(regex=ICX_ADDRESS_REGEX),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=25, le=100),
    refresh: bool = True,
):
    return TEMPLATES.TemplateResponse(
        "address/index.html",
        {
            "request": request,
            "title": f"{address[:8]}... | RHIZOME Tracker",
            "address": address,
            "page": page,
            "limit": limit,
            "refresh": refresh,
        },
    )


@app.get(
    "/block/{block_height}/",
    status_code=status.HTTP_200_OK,
    tags=["app"],
)
def get_block(
    request: Request,
    block_height: int = Path(ge=1),
):
    return


@app.get(
    "/btp/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    tags=["app"],
)
async def index(request: Request):

    return TEMPLATES.TemplateResponse(
        "btp/index.html",
        {
            "request": request,
            "title": "BTP & ICON Bridge",
        },
    )


@app.get("/build/", tags=["app"])
async def get_build(request: Request):
    return TEMPLATES.TemplateResponse(
        "build/index.html",
        {
            "request": request,
            "title": "Build",
        },
    )


@app.get(
    "/dapps/",
    status_code=status.HTTP_200_OK,
    tags=["app"],
)
def get_dapps(request: Request):
    return TEMPLATES.TemplateResponse(
        "dapps/index.html",
        {
            "request": request,
            "title": "ICON dApps",
        },
    )


@app.get(
    "/addresses/",
    status_code=status.HTTP_200_OK,
    tags=["app"],
)
def get_addresses(
    request: Request,
    page: int = Query(default=1, ge=1),
):
    return TEMPLATES.TemplateResponse(
        "addresses/index.html",
        {
            "request": request,
            "title": "Addresses",
            "page": page,
        },
    )


@app.get(
    "/contract/{address}/",
    status_code=status.HTTP_200_OK,
    tags=["app"],
)
def get_contract(
    request: Request,
    address: str = Path(regex="^cx[a-fA-F0-9]{40}$"),
):
    return TEMPLATES.TemplateResponse(
        "contract/index.html",
        {
            "request": request,
            "title": "Contract",
        },
    )


@app.get(
    "/contracts/",
    status_code=status.HTTP_200_OK,
    tags=["app"],
)
async def get_contracts(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=25),
):
    return TEMPLATES.TemplateResponse(
        "contracts/index.html",
        {"request": request, "title": "Contracts", "page": page, "limit": limit},
    )


@app.get(
    "/governance/",
    status_code=status.HTTP_200_OK,
    tags=["app"],
)
def get_contracts(request: Request):
    return TEMPLATES.TemplateResponse(
        "governance/index.html",
        {
            "request": request,
            "title": "Governance",
        },
    )


@app.get("/tokens/", status_code=status.HTTP_200_OK, tags=["app"])
def get_tokens(request: Request, page: int = Query(default=1, ge=1)):
    return TEMPLATES.TemplateResponse(
        "tokens/index.html",
        {"request": request, "title": "Tokens", "page": page},
    )


@app.get("/transaction/{tx_hash}/", status_code=status.HTTP_200_OK, tags=["app"])
async def get_transaction(
    request: Request, tx_hash: str = Path(regex=ICX_TX_HASH_REGEX)
):
    transaction = await Tracker.get_transaction_details(tx_hash)
    logs = await Tracker.get_transaction_logs(tx_hash)

    # Initialize transaction summary variable.
    tx_summary = None

    # Parse specific transactions to generate transaction summary.
    # Balanced Loans (cx66d4d90f5f113eba575bf793570135f9b10cece1)
    if transaction.to_address == "cx66d4d90f5f113eba575bf793570135f9b10cece1":

        # A liquidation of a Balanced loan position.
        if transaction.method == "liquidate":
            liquidator_address = transaction.from_address
            position_owner_address = transaction.data["default"]["params"]["_owner"]

            if transaction.log_count == 0:  # Unsuccessful liquidation.
                tx_summary = f"This transaction was sent by {liquidator_address} to liquidate a Balanced loan position owned by {position_owner_address}. The liquidation was unsuccessful because the transaction was too slow."
            else:  # Successful liquidation.
                liquidated_amount = int(json.loads(logs[3].indexed)[2], 16) / 10**18
                liquidated_amount = format_number(liquidated_amount, 4)
                tx_summary = f"This transaction was sent by {liquidator_address} to liquidate a Balanced loan position owned by {position_owner_address}. The liquidation was successful, and resulted in the position owner losing {liquidated_amount} sICX."

    return TEMPLATES.TemplateResponse(
        "transaction/index.html",
        {
            "request": request,
            "title": "Transaction",
            "tx_hash": tx_hash,
            "transaction": transaction,
            "tx_summary": tx_summary,
            "logs": logs,
        },
    )


@app.get("/transactions/", status_code=status.HTTP_200_OK, tags=["app"])
async def get_transactions(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=25, le=100),
    refresh: bool = True,
):
    return TEMPLATES.TemplateResponse(
        "transactions/index.html",
        {
            "request": request,
            "title": "Transactions",
            "page": page,
            "limit": limit,
            "refresh": refresh,
        },
    )


@app.get("/validator/{address}/", status_code=status.HTTP_200_OK, tags=["app"])
async def get_validator(
    request: Request, address: str = Path(regex="^hx[a-fA-F0-9]{40}$")
):
    return TEMPLATES.TemplateResponse(
        "validator/index.html",
        {"request": request, "title": "Transactions"},
    )


########
# MISC #
########


@app.post("/search/", tags=["app"])
async def search(search: str = Form()):
    try:
        if search.startswith("hx") and len(search) == 42:
            redirect_url = f"/address/{search}/"
        elif search.startswith("cx") and len(search) == 42:
            redirect_url = f"/contract/{search}/"
        elif search.startswith("0x") and len(search) == 66:
            redirect_url = f"/transaction/{search}/"
        elif (
            int(search) > 0
            and int(search) <= (await Icx().get_latest_block())["height"]
        ):
            redirect_url = f"/block/{search}/"
        else:
            redirect_url = "/404/"
    except ValueError:
        pass
    else:
        return Response(headers={"hx-redirect": redirect_url})


@app.get("/status/", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_status(request: Request):
    r = await HttpReq.head(f'{ENV["API_URL"]}/status/', timeout=2, retries=1)
    if r.status_code == 204:
        service_status = 1
    else:
        service_status = 0
    return TEMPLATES.TemplateResponse(
        "status.html", {"request": request, "service_status": service_status}
    )


@app.get("/health-check/", status_code=status.HTTP_200_OK, response_class=Response)
async def health_check():
    return "OK"


@app.get("/404/", status_code=status.HTTP_404_NOT_FOUND)
async def get_404(request: Request):
    return TEMPLATES.TemplateResponse("errors/404.html", {"request": request})


@app.exception_handler(StarletteHTTPException)
async def custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        if str(request.url.path).startswith("/assets/validators/"):
            return RedirectResponse("/assets/validators/validator_128px.png")
        elif str(request.url.path).startswith("/assets/tokens/"):
            return RedirectResponse("/assets/validators/validator_128px.png")
        else:
            return TEMPLATES.TemplateResponse(
                "errors/404.html",
                {"request": request},
                status_code=status.HTTP_404_NOT_FOUND,
            )
    else:
        return await http_exception_handler(request, exc)


@app.on_event("startup")
async def app_init():
    db_client = AsyncIOMotorClient(ENV["DB_URL"])
    await init_beanie(
        db_client[ENV["DB_NAME"]],
        document_models=[
            Db_BalancedLoan,
            Db_IcxBlock,
            Db_RecentBlock,
            Db_GithubCommit,
            Db_GithubReleases,
            Db_GithubRepo,
            Db_IcxSicxBnusdQuote,
            Db_BalancedPoolDynamicDataSnapshot,
            Db_BalancedPoolStaticData,
            Db_ValidatorNodeStatus,
            Db_RecentTransaction,
        ],
    )
