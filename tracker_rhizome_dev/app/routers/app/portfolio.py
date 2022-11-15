from fastapi import APIRouter, Request, Response, status
from fastapi.exceptions import HTTPException
from tracker_rhizome_dev import TEMPLATES

router = APIRouter(prefix="/portfolio")


@router.get("/")
async def get_portfolio(request: Request):
    return


@router.get("/{address}/")
async def get_portfolio_address(request: Request):
    return
