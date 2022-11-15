from datetime import timedelta

from fastapi import APIRouter, Request, status
from fastapi.exceptions import HTTPException
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.models.icx import Db_IcxSicxBnusdQuote

router = APIRouter(prefix="/icx")


@router.get("/icx-sicx-bnusd-quotes/")
async def get_icx_sicx_bnusd_quotes(
    request: Request, time_value: int, time_precision: str
):
    if time_precision not in ["minute", "hour", "day"]:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail='Valid time_precision values are "minute", "hour", and "day".',
        )
    latest_quote = (
        await Db_IcxSicxBnusdQuote.find().sort(-Db_IcxSicxBnusdQuote.id).first_or_none()
    )
    precision_in_seconds = {"minute": 60, "hour": 3600, "day": 86400}

    end_time = latest_quote.id
    start_time = end_time - timedelta(
        seconds=time_value * precision_in_seconds[time_precision]
    )

    quotes = await Db_IcxSicxBnusdQuote.find(
        Db_IcxSicxBnusdQuote.id >= start_time, Db_IcxSicxBnusdQuote.id < end_time
    ).to_list()

    return {"count": len(quotes), "data": quotes}


@router.get("/latest-block/", status_code=status.HTTP_200_OK)
async def get_latest_block(request: Request, height_only: bool = False):
    block = Icx.get_block("latest")
    if height_only is True:
        return {"data": block["height"]}
    else:
        return {"data": block}
