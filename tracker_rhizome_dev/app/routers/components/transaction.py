from fastapi import APIRouter, Path, Query, Request, status
from fastapi.responses import HTMLResponse

from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.regex import ICX_TX_HASH_REGEX
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import format_number

router = APIRouter(prefix="/transaction")


@router.get(
    "/confirmations/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    tags=["component"],
)
async def get_confirmations(
    request: Request,
    tx_block_height: int,
):
    current_block_height = Icx.get_block("latest", height_only=True)
    confirmations = current_block_height - tx_block_height
    confirmations = format_number(confirmations)
    return TEMPLATES.TemplateResponse(
        "transaction/components/confirmations.html",
        {
            "request": request,
            "confirmations": confirmations,
        },
    )


@router.get(
    "/logs/{tx_hash}/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    tags=["component"],
)
async def get_logs(
    request: Request,
    tx_hash: str = Path(regex=ICX_TX_HASH_REGEX),
):
    logs = await Tracker.get_transaction_logs(tx_hash)
    if logs is not None:
        return TEMPLATES.TemplateResponse(
            "transaction/components/logs.html",
            {
                "request": request,
                "logs": logs,
            },
        )
