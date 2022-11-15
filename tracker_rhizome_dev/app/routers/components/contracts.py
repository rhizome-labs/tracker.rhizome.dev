from fastapi import APIRouter, Query, Request, status
from fastapi.responses import HTMLResponse
from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import calculate_skip

router = APIRouter(prefix="/contracts")


@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_contracts(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=100, ge=25),
):
    contracts = await Tracker.get_contracts(limit, calculate_skip(page, limit))
    return TEMPLATES.TemplateResponse(
        "contracts/components/contracts.html",
        {
            "request": request,
            "page": page,
            "limit": limit,
            "contracts": contracts,
        },
    )
