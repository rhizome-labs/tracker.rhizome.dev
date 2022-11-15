from fastapi import APIRouter, Request, Response, status
from fastapi.exceptions import HTTPException
from tracker_rhizome_dev import TEMPLATES

router = APIRouter(prefix="/dapps")


@router.get("/balanced/")
async def get_dapps_balanced(request: Request):
    return TEMPLATES.TemplateResponse(
        "balanced/index.html",
        {
            "request": request,
            "title": "Balanced",
        },
    )


@router.get("/balanced/liquidations/")
async def get_dapps_balanced_liquidations(request: Request):
    return TEMPLATES.TemplateResponse(
        "balanced/liquidations.html",
        {
            "request": request,
            "title": "Balanced Liquidations",
        },
    )


@router.get("/balanced/loans/")
async def get_dapps_balanced_loans(request: Request):
    return TEMPLATES.TemplateResponse(
        "balanced/loans.html",
        {
            "request": request,
            "title": "Balanced",
        },
    )
