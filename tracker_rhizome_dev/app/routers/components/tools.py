from fastapi import APIRouter, Path, Query, Request, status
from fastapi.responses import HTMLResponse

from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.regex import ICX_TX_HASH_REGEX
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import format_number

router = APIRouter(prefix="/tools")


@router.get(
    "/historical-staking-reward-calculator/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    tags=["component"],
)
async def get_historical_staking_reward_calculator(
    request: Request,
    address: str,
):
    iscore_claims_tx = await Tracker.get_transactions(
        from_address=address,
        method="claimIScore",
    )
    iscore_claims_tx_hashes = [transaction.hash for transaction in iscore_claims_tx]
    print(iscore_claims_tx_hashes)
    return
