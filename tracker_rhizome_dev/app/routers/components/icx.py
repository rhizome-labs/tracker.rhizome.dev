import json

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.http_request import HttpReq
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import calculate_average_block_time, format_number

router = APIRouter(prefix="/icx")


@router.get(
    "/average-block-time/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_average_block_time(request: Request):
    transactions = await Tracker.get_transactions(limit=50, format=False)
    block_timestamps = [transaction["block_timestamp"] for transaction in transactions]
    average_block_time = calculate_average_block_time(block_timestamps)
    return TEMPLATES.TemplateResponse(
        "partials/module.html",
        {
            "request": request,
            "id": "average-block-time",
            "body": f"{average_block_time:.4}s",
            "title": "Block Time",
        },
    )


@router.get(
    "/icx-usd-price/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_icx_usd_price(request: Request):
    icx_usd_price = Icx.get_icx_usd_price()
    return TEMPLATES.TemplateResponse(
        "partials/module.html",
        {
            "request": request,
            "id": "icx-usd-price",
            "body": f"${format_number(icx_usd_price)}",
            "title": "ICX Price",
        },
    )


@router.get(
    "/total-token-transfers/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_total_token_transfers(request: Request):
    token_transfers = await Tracker.get_total_token_transfers()
    return TEMPLATES.TemplateResponse(
        "partials/module.html",
        {
            "request": request,
            "id": "token-transfers",
            "body": format_number(token_transfers),
            "title": "Total IRC-2 Tx",
        },
    )


@router.get(
    "/total-transactions/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_total_transactions(request: Request):
    total_transactions = await Tracker.get_total_transactions()
    return TEMPLATES.TemplateResponse(
        "partials/module.html",
        {
            "request": request,
            "id": "total-transactions",
            "body": format_number(total_transactions),
            "title": "Total Tx",
        },
    )
