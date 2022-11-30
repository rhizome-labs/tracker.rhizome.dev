from datetime import datetime

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import HTMLResponse

from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.data.addresses import Addresses
from tracker_rhizome_dev.app.http_request import HttpReq
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import format_number

router = APIRouter(prefix="/transactions")


@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_transactions(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=25, le=100),
    refresh: bool = True,
):
    skip = int((page - 1) * limit)
    transactions = await Tracker.get_transactions(skip=skip, limit=limit)
    return TEMPLATES.TemplateResponse(
        "transactions/components/transactions.html",
        {
            "request": request,
            "title": "Transactions",
            "page": page,
            "limit": limit,
            "refresh": refresh,
            "transactions": transactions,
        },
    )


@router.get(
    "/total-transactions/", response_class=HTMLResponse, status_code=status.HTTP_200_OK
)
async def get_total_transactions(request: Request):
    total_transactions = await Tracker.get_total_transactions()
    return TEMPLATES.TemplateResponse(
        "transactions/components/total_transactions.html",
        {
            "request": request,
            "title": "Total Tx",
            "total_transactions": format_number(total_transactions),
        },
    )


@router.get(
    "/total-token-transfers/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_total_token_transfers(request: Request):
    url = f'{ENV["API_URL"]}/transactions/total-token-transfers/'
    r = await HttpReq.get(url)
    data = r.json()
    total_token_transfers = data["data"]
    return TEMPLATES.TemplateResponse(
        "transactions/components/total_token_transfers.html",
        {
            "request": request,
            "title": "Token Tx",
            "total_token_transfers": format_number(total_token_transfers),
        },
    )
