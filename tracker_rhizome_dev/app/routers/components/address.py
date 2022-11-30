from fastapi import APIRouter, Path, Query, Request, status
from fastapi.responses import HTMLResponse

from tracker_rhizome_dev import TEMPLATES
from tracker_rhizome_dev.app.regex import ICX_ADDRESS_REGEX
from tracker_rhizome_dev.app.tracker import Tracker

router = APIRouter(prefix="/address")


@router.get(
    "/overview/{address}/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_address_overview(
    request: Request,
    format: str = Query("html"),
    address: str = Path(regex=ICX_ADDRESS_REGEX),
):
    address_details = await Tracker.get_address_details(address)

    if format == "json":
        pass
    else:
        return TEMPLATES.TemplateResponse(
            "address/components/overview.html",
            {
                "request": request,
                "data": address_details,
            },
        )


@router.get(
    "/transactions/{address}/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_address_transactions(
    request: Request,
    address: str = Path(regex=ICX_ADDRESS_REGEX),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=25, le=100),
    refresh: bool = True,
):
    skip = int((page - 1) * limit)
    transactions = await Tracker.get_address_transactions(address, limit, skip)
    return TEMPLATES.TemplateResponse(
        "address/components/transactions.html",
        {
            "request": request,
            "page": page,
            "limit": limit,
            "refresh": refresh,
            "transactions": transactions,
        },
    )
