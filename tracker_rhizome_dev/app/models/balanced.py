import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Union

import pymongo
from beanie import Document, Indexed
from pydantic import BaseModel, root_validator, validator

from tracker_rhizome_dev import EXA
from tracker_rhizome_dev.app.data.country_codes import CountryCodes
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.utils import format_number, format_percentage, to_int

###################
# Database Models #
###################

# balancedPoolDynamicData


class Db_BalancedPoolDynamicData(BaseModel):
    id: int
    base: Decimal
    price: Decimal
    price_daily_change_amount: Decimal
    price_daily_change_percent: Decimal
    quote: Decimal
    total_supply: Decimal


class Db_BalancedPoolDynamicDataSnapshot(Document):
    id: datetime
    data: List[Db_BalancedPoolDynamicData]

    class Settings:
        name = "balancedPoolDynamicData"


# balancedPoolStaticData


class Db_BalancedPoolStaticData(Document):
    id: int
    base_decimals: int
    base_name: str
    base_token: str
    base_symbol: str = None
    min_quote: Decimal
    pool_name: str = None
    quote_decimals: int
    quote_name: str
    quote_token: Union[str, None]
    quote_symbol: str = None

    class Settings:
        name = "balancedPoolStaticData"


class BalancedLoanAssets(BaseModel):
    bnusd: Union[Decimal, None]
    sicx: Union[Decimal, None]

    @root_validator(pre=True)
    def root_validator(cls, values):
        try:
            values["bnusd"] = to_int(values["bnUSD"]) / EXA
            values["sicx"] = to_int(values["sICX"]) / EXA
        except:
            values["bnusd"] = 0
            values["sicx"] = 0
        return values


class BalancedLoanHolding(BaseModel):
    bnUSD: str
    sICX: str

    @validator("bnUSD")
    def validate_bnusd(cls, v):
        return Decimal(to_int(v)) / EXA

    @validator("sICX")
    def validate_sicx(cls, v):
        return Decimal(to_int(v)) / EXA


class BalancedLoanHoldings(BaseModel):
    sICX: BalancedLoanHolding


class BalancedLoanStanding(BaseModel):
    collateral: Decimal
    ratio: Decimal
    standing: str
    total_debt: Decimal

    @root_validator(pre=True)
    def root_validator(cls, values):

        for k, v in values.items():
            try:
                values[k] = to_int(v)
            except:
                continue

        return values

    @validator("collateral")
    def validate_collateral(cls, v):
        return Decimal(v) / EXA

    @validator("ratio")
    def validate_ratio(cls, v):
        return Decimal(v) / EXA

    @validator("total_debt")
    def validate_total_debt(cls, v):
        return Decimal(v) / EXA


class BalancedLoanStandings(BaseModel):
    sICX: BalancedLoanStanding


class BalancedLoan(BaseModel):
    address: str
    assets: BalancedLoanAssets
    collateral: Decimal
    created: datetime
    holdings: BalancedLoanHoldings
    pos_id: int
    ratio: Decimal
    standings: BalancedLoanStandings
    total_debt: Decimal

    @root_validator(pre=True)
    def root_validator(cls, values):

        for k, v in values.items():
            try:
                values[k] = to_int(v)
            except:
                continue

        values["created"] = datetime.utcfromtimestamp(int(values["created"] / 1000000))
        values["collateral"] = Decimal(values["collateral"]) / EXA
        values["ratio"] = Decimal(values["ratio"]) / EXA
        values["total_debt"] = Decimal(values["total_debt"]) / EXA

        return values


class Db_BalancedLiquidation(Document):
    id: str
    tx_hash: str
    date: datetime
    block_height: int
    amount: Decimal
    liquidator: str

    class Settings:
        name = "balancedLoans"


class Db_BalancedLoan(Document):
    id: int
    address: str
    assets: BalancedLoanAssets
    collateral: Decimal
    created: datetime
    holdings: BalancedLoanHoldings
    ratio: Decimal
    standings: BalancedLoanStandings
    total_debt: Decimal

    class Settings:
        name = "balancedLoans"
        use_cache = True
        cache_expiration_time = timedelta(seconds=30)
        cache_capacity = 5


class App_BalancedLoan(BaseModel):
    id: int
    address: str
    assets: BalancedLoanAssets
    collateral: Decimal
    created: datetime
    holdings: BalancedLoanHoldings
    ratio: Decimal
    standings: BalancedLoanStandings
    total_debt: Decimal

    @validator("collateral")
    def validate_collateral(cls, v):
        return {
            "raw": v,
            "formatted": format_number(v),
        }

    @validator("id")
    def validate_id(cls, v):
        return {
            "raw": v,
            "formatted": format_number(v),
        }

    @validator("ratio")
    def validate_ratio(cls, v):
        return {
            "raw": v,
            "formatted": format_percentage(v),
        }

    @validator("total_debt")
    def validate_total_debt(cls, v):
        return {
            "raw": v,
            "formatted": format_number(v),
        }


class Db_BalancedLoanShortView(BaseModel):
    ratio: Decimal
    total_debt: Decimal


class App_BalancedLiquidation(BaseModel):
    address: str
    block_number: int
    block_timestamp: int
    amount: float
    log_index: int
    method: str
    transaction_hash: str

    @root_validator(pre=True)
    def root_validator(cls, values):
        values["address"] = values["indexed"][1]
        values["amount"] = to_int(values["indexed"][2]) / EXA
        return values

    @validator("block_timestamp")
    def validate_timestamp(cls, v):
        return {"raw": v, "formatted": datetime.utcfromtimestamp(int(v / 1000000))}

    @validator("amount")
    def validate_amount(cls, v):
        return {"raw": v, "formatted": format_number(v)}
