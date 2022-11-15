from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.http_request import HttpReq

router = APIRouter(prefix="/charts")


@router.get(
    "/bnusd-usd-price-chart/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_bnusd_usd_price_chart(request: Request):
    url = f'{ENV["API_URL"]}/charts/bnusd-usd-quotes/'
    r = await HttpReq.get(url)
    data = r.json()
    quotes = data["data"]
    return TEMPLATES.TemplateResponse(
        "balanced/components/bnusd_usd_price_chart.html",
        {"request": request, "quotes": quotes},
    )
