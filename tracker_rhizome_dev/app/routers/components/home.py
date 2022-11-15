from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.http_request import HttpReq
from tracker_rhizome_dev.app.models.icx import Db_RecentBlock, RecentBlock, Transaction
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import format_number, format_percentage

router = APIRouter(prefix="/home")


@router.get(
    "/block-stream/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_block_stream(request: Request, limit: int = 20):
    """
    Renders a horizontal stream of blocks on the ICON blockchain.
    """
    # Force 50 as limit.
    if limit > 50:
        limit = 50

    result = (
        await Db_RecentBlock.find_all().limit(limit).sort(-Db_RecentBlock.id).to_list()
    )
    blocks = [RecentBlock(hash=block.hash, number=block.id) for block in result]
    return TEMPLATES.TemplateResponse(
        "home/components/block_stream.html",
        {
            "request": request,
            "blocks": blocks,
        },
    )


# @router.get(
#    "/latest-transactions/",
#    status_code=status.HTTP_200_OK,
#    response_class=HTMLResponse,
# )
# async def get_latest_transactions(request: Request, limit: int = 20):
#    transactions = await Tracker.get_transactions(limit=limit)
#    transactions = [Transaction(**transaction) for transaction in transactions]
#    return TEMPLATES.TemplateResponse(
#        "home/components/latest_transactions.html",
#        {
#            "request": request,
#            "transactions": transactions,
#        },
#    )


@router.get(
    "/latest-token-transfers/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_latest_token_transfers(request: Request, limit: int = 20):
    token_transfers = await Tracker.get_token_transfers(limit=limit)
    return TEMPLATES.TemplateResponse(
        "home/components/latest_token_transfers.html",
        {
            "request": request,
            "transactions": token_transfers,
        },
    )
