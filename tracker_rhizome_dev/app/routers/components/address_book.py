from statistics import mean

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from rich import inspect
from tracker_rhizome_dev import ENV, TEMPLATES

router = APIRouter(prefix="/address-book")


@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_address_book(request: Request):
    params = request.query_params

    address_book = {}
    for param in params:
        address_book[param] = params[param]

    return TEMPLATES.TemplateResponse(
        "address_book/components/address_book.html",
        {"request": request, "address_book": address_book},
    )


@router.post("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def post_address_book(request: Request):
    form_data = await request.form()

    icx_address = form_data["icx-address"]
    name = form_data["name"]

    return TEMPLATES.TemplateResponse(
        "address_book/components/register_address.html",
        {"request": request, "icx_address": icx_address, "name": name},
    )
