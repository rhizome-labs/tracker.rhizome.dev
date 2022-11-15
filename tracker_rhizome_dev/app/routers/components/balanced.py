from statistics import mean

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import HTMLResponse

from tracker_rhizome_dev import ENV, TEMPLATES
from tracker_rhizome_dev.app.balanced import Balanced
from tracker_rhizome_dev.app.balanced_api import BalancedApi
from tracker_rhizome_dev.app.http_request import HttpReq
from tracker_rhizome_dev.app.models.balanced import (App_BalancedLiquidation,
                                                     App_BalancedLoan,
                                                     Db_BalancedLoan)
from tracker_rhizome_dev.app.utils import format_number, format_percentage

router = APIRouter(prefix="/balanced")


@router.get(
    "/dao-fund-balance-sheet/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_dao_fund_balance_sheet(request: Request):
    assets = await BalancedApi.get_daofund_balanced_sheet()
    for asset in assets:
        asset["amount"] = format_number(asset["amount"])
    assets.sort(key=lambda k: k["symbol"].casefold())
    return TEMPLATES.TemplateResponse(
        "balanced/components/dao_fund_balanced_sheet.html",
        {"request": request, "assets": assets},
    )


@router.get(
    "/liquidations/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_liquidations(request: Request, page: int = 1):
    liquidations = await Balanced.get_liquidations(page=page)
    liquidations = [
        App_BalancedLiquidation(**dict(liquidation)) for liquidation in liquidations
    ]
    return TEMPLATES.TemplateResponse(
        "balanced/components/liquidations.html",
        {"request": request, "liquidations": liquidations, "page": page},
    )

@router.get("/loans/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_loans(
    request: Request,
    sort_by: str = Query(
        default="id",
        regex=r"^id$|^ratio$|^collateral$|^debt$|^date$|^status$",
    ),
    sort_dir: str = "asc",
    show_liquidated: bool = False,
):
    if show_liquidated is True:
        loans = await Db_BalancedLoan.find().to_list()
    else:
        loans = await Db_BalancedLoan.find(Db_BalancedLoan.ratio > 0).to_list()

    if sort_dir == "desc":
        reverse = True
    else:
        reverse = False

    if sort_by == "id":
        loans.sort(key=lambda x: x.id, reverse=reverse)
    elif sort_by == "collateral":
        loans.sort(key=lambda x: x.collateral, reverse=reverse)
    elif sort_by == "debt":
        loans.sort(key=lambda x: x.total_debt, reverse=reverse)
    elif sort_by == "ratio":
        loans.sort(key=lambda x: x.ratio, reverse=reverse)
    elif sort_by == "date":
        loans.sort(key=lambda x: x.created, reverse=reverse)
    elif sort_by == "status":
        loans.sort(key=lambda x: x.standing, reverse=reverse)

    loans = [App_BalancedLoan(**dict(loan)) for loan in loans]

    return TEMPLATES.TemplateResponse(
        "balanced/components/loans.html",
        {
            "request": request,
            "loans": loans,
            "loan_count": format_number(len(loans) - 1),
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "show_liquidated": show_liquidated,
        },
    )


@router.get(
    "/loans/overview/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_loans_overview(request: Request):

    loans = await Db_BalancedLoan.find_all().to_list()
    loan_count = len(loans)
    mean_ratio = mean([loan.ratio for loan in loans])
    max_ratio = max([loan.ratio for loan in loans])

    loan_collateral = Balanced.get_loan_collateral()

    return TEMPLATES.TemplateResponse(
        "balanced/components/loans_overview.html",
        {
            "request": request,
            "loan_count": format_number(loan_count),
            "total_collateral": format_number(loan_collateral, precision=0),
            "mean_ratio": format_percentage(mean_ratio / 100),
            "max_ratio": format_percentage(max_ratio / 100),
        },
    )


@router.get(
    "/stability-fund/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_stability_fund(request: Request):
    stability_fund = Balanced.get_stability_fund()
    stability_fund = [(asset[0], format_number(asset[1])) for asset in stability_fund]
    return TEMPLATES.TemplateResponse(
        "balanced/components/stability_fund.html",
        {"request": request, "stability_fund": stability_fund},
    )


@router.get("/pools/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_pools(request: Request):
    balanced = Balanced()
    pools = balanced.get_pools()
    for pool in pools:
        pool["base"] = (pool["base"], format_number(pool["base"]))
        pool["quote"] = (pool["quote"], format_number(pool["quote"]))
        pool["price"] = (pool["price"], format_number(pool["price"]))
        pool["total_supply"] = (
            pool["total_supply"],
            format_number(pool["total_supply"]),
        )
        pool["price_daily_change_amount"] = (
            pool["price_daily_change_amount"],
            format_number(pool["price_daily_change_amount"], display_sign=True),
        )
        pool["price_daily_change_percent"] = (
            pool["price_daily_change_percent"],
            format_percentage(pool["price_daily_change_percent"], display_sign=True),
        )
        if pool["id"] == 5:
            print(pool)

    return TEMPLATES.TemplateResponse(
        "balanced/components/pools.html",
        {"request": request, "pools": pools},
    )