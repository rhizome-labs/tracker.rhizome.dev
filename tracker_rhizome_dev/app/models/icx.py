import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Union

import pymongo
import timeago
from beanie import Document
from pydantic import BaseModel, root_validator, validator

from tracker_rhizome_dev import EXA
from tracker_rhizome_dev.app.cps import Cps
from tracker_rhizome_dev.app.data.addresses import Addresses
from tracker_rhizome_dev.app.data.country_codes import CountryCodes
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.utils import (
    format_number,
    format_percentage,
    to_int,
    to_relative_time,
)


class Db_RecentBlock(Document):
    id: int
    hash: str

    class Settings:
        name = "recentBlocks"
        use_cache = True
        cache_expiration_time = timedelta(seconds=2)


class RecentBlock(BaseModel):
    hash: str
    number: int

    @validator("number")
    def validate_block_number(cls, v):
        return {"default": v, "formatted": format_number(v)}


class Block(Document):
    hash: str
    number: int
    peer_id: str
    timestamp: int
    transaction_amount: str
    transaction_count: int
    transaction_fees: str

    @validator("number")
    def validate_block_number(cls, v):
        return {"default": v, "formatted": format_number(v)}

    @validator("transaction_amount")
    def validate_amount(cls, v):
        amount = Decimal(to_int(v)) / EXA
        return {"default": amount, "formatted": format_number(amount)}

    @validator("transaction_fees")
    def validate_transaction_fees(cls, v):
        fees = Decimal(to_int(v)) / EXA
        return {"default": fees, "formatted": format_number(fees)}


class Contract(BaseModel):
    address: str
    balance: int
    created_timestamp: int
    is_token: bool
    log_count: int
    name: str
    status: str
    token_standard: str
    transaction_count: int

    @validator("balance")
    def validate_balance(cls, v):
        return {"default": v, "formatted": format_number(v)}

    @validator("created_timestamp")
    def validate_created_timestamp(cls, v):
        timestamp_in_s = int(v / 1000000)
        dt_utc = datetime.utcfromtimestamp(timestamp_in_s)
        return {
            "default": timestamp_in_s,
            "formatted": dt_utc,
        }

    @validator("transaction_count")
    def validate_transaction_count(cls, v):
        return {"default": v, "formatted": format_number(v)}


class Log(BaseModel):
    address: str
    block_number: int
    block_timestamp: int
    data: str
    indexed: str
    log_index: int
    method: str
    transaction_hash: str

    @validator("data")
    def validate_data(cls, v):
        return json.loads(v)

    @validator("indexed")
    def validate_indexed(cls, v):
        return json.loads(v)


class TokenTransfer(BaseModel):
    block_number: int
    block_timestamp: int
    from_address: str
    log_index: int
    to_address: str
    token_contract_address: str
    token_contract_name: str
    token_contract_symbol: str
    transaction_fee: str
    transaction_hash: str
    value: str
    value_decimal: float

    @validator("block_timestamp")
    def validate_block_timestamp(cls, v):
        timestamp_in_s = int(v / 1000000)
        dt_utc = datetime.utcfromtimestamp(timestamp_in_s)
        return {
            "default": timestamp_in_s,
            "formatted": dt_utc,
            "relative": to_relative_time(dt_utc),
        }

    @validator("value_decimal")
    def validate_value_decimal(cls, v):
        return {"default": v, "formatted": format_number(v)}


class Db_RecentTransaction(Document):
    id: str  # transaction hash
    block_timestamp: int
    value: str
    method: str

    class Settings:
        name = "recentTransactions"

    @validator("block_timestamp")
    def validate_block_timestamp(cls, v):
        timestamp_in_s = int(v / 1000000)
        return {
            "default": timestamp_in_s,
            "formatted": datetime.utcfromtimestamp(timestamp_in_s),
        }

    @validator("method")
    def validate_method(cls, v):
        if v == "":
            return None
        else:
            return v

    @validator("value")
    def validate_value(cls, v):
        if v == "":
            return 0
        else:
            return Decimal(to_int(v)) / Decimal(EXA)


class Transaction(BaseModel):
    block_number: int
    block_timestamp: int
    data: str
    from_address: str
    hash: str
    method: str
    status: str
    to_address: str
    transaction_fee: str
    transaction_type: int
    value: str

    @validator("from_address", "to_address")
    def validate_address(cls, v):
        if v == "":
            v = None
        return {
            "default": v,
            "formatted": Addresses.get_address_name(v),
            "type": Addresses.get_address_type(v),
        }

    @validator("block_number")
    def validate_block_number(cls, v):
        return {
            "default": v,
            "formatted": format_number(v),
        }

    @validator("block_timestamp")
    def validate_block_timestamp(cls, v):
        timestamp_in_s = int(v / 1000000)
        return {
            "default": timestamp_in_s,
            "formatted": datetime.utcfromtimestamp(timestamp_in_s),
        }

    @validator("data")
    def validate_data(cls, v):
        if v == "":
            return {"default": None, "formatted": None}
        else:
            data = json.loads(v)
            return {
                "default": data,
                "formatted": json.dumps(data, indent=4),
            }

    @validator("method")
    def validate_method(cls, v):
        if v == "":
            v = None
        return v

    @validator("value")
    def validate_value(cls, v):
        if v == "":
            v = 0
        else:
            v = to_int(v) / EXA
        return {
            "default": v,
            "formatted": format_number(v),
        }

    @validator("transaction_fee")
    def validate_fee(cls, v):
        if v == "":
            v = 0
        else:
            v = to_int(v) / EXA
        return {
            "default": v,
            "formatted": format_number(v),
        }


class TransactionDetail(BaseModel):
    block_hash: str
    block_number: int
    block_timestamp: int
    confirmations: Union[int, None]
    cumulative_step_used: int
    data: str
    data_type: str
    from_address: Union[str, None]
    hash: str
    log_count: int
    log_index: int
    logs_bloom: str
    method: Union[str, None]
    nid: int
    nonce: Union[int, None]
    score_address: str
    signature: Union[str, None]
    status: int
    step_limit: int
    step_price: int
    step_used: int
    timestamp: int
    to_address: Union[str, None]
    transaction_fee: int
    transaction_index: int
    type: str
    value: int
    version: int

    @root_validator(pre=True)
    def root_validator(cls, values):
        for k, v in values.items():
            try:
                if v.startswith("0x"):
                    _v = to_int(v)
                    values[k] = _v
                    if k in ["bonded", "bonded", "delegated", "irep", "power"]:
                        values[k] = Decimal(_v) / EXA
            except AttributeError:
                pass

        current_block_height = Icx.get_block("latest")["height"]
        values["confirmations"] = current_block_height - values["block_number"]

        for k in ["method", "nonce", "from_address", "signature", "to_address"]:
            if values[k] == "":
                values[k] = None

        for k in ["nid", "value", "step_limit"]:
            if values[k] == "":
                values[k] = 0

        return dict(sorted(values.items()))

    @validator("block_number")
    def validate_block_number(cls, v):
        return {
            "default": v,
            "formatted": format_number(v),
        }

    @validator("block_timestamp")
    def validate_block_timestamp(cls, v):
        timestamp_in_s = int(v / 1000000)
        return {
            "default": timestamp_in_s,
            "formatted": datetime.utcfromtimestamp(timestamp_in_s),
        }

    @validator("confirmations")
    def validate_confirmations(cls, v):
        return {
            "default": v,
            "formatted": format_number(v),
        }

    @validator("cumulative_step_used")
    def validate_cumulative_step_used(cls, v):
        return {"default": v, "formatted": format_number(v)}

    @validator("data")
    def validate_data(cls, v):
        if v == "":
            return {"default": None, "formatted": None}
        else:
            data = json.loads(v)
            return {
                "default": data,
                "formatted": json.dumps(data, indent=4),
            }

    @validator("nonce")
    def validate_nonce(cls, v):
        if v is not None:
            return {"default": v, "formatted": format_number(v)}
        else:
            return None

    @validator("step_limit")
    def validate_step_limit(cls, v):
        return {"default": v, "formatted": format_number(v)}

    @validator("step_price")
    def validate_step_price(cls, v):
        step_price = Decimal(v) / EXA
        return {"default": step_price, "formatted": format_number(step_price)}

    @validator("step_used")
    def validate_step_used(cls, v):
        return {"default": v, "formatted": format_number(v)}

    @validator("timestamp")
    def validate_timestamp(cls, v):
        timestamp_in_s = int(v / 1000000)
        return {
            "default": timestamp_in_s,
            "formatted": datetime.utcfromtimestamp(timestamp_in_s),
        }

    @validator("transaction_fee")
    def validate_transaction_fee(cls, v):
        transaction_fee = Decimal(v) / EXA
        return {"default": transaction_fee, "formatted": format_number(transaction_fee)}

    @validator("value")
    def validate_value(cls, v):
        value = Decimal(v) / EXA
        return {"default": value, "formatted": format_number(value)}


class TransactionLog(BaseModel):
    address: str
    block_number: int
    block_timestamp: int
    data: str
    data_int: str
    indexed: str
    log_index: int
    method: str
    tx_hash: str

    @root_validator(pre=True)
    def root_validator(cls, values):
        values["tx_hash"] = values["transaction_hash"]
        values["data_int"] = values["data"]
        return values

    @validator("block_timestamp")
    def validate_block_timestamp(cls, v):
        timestamp = int(v / 1000000)
        return {"default": timestamp, "formatted": datetime.utcfromtimestamp(timestamp)}

    @validator("block_number")
    def validate_block_number(cls, v):
        return {"default": v, "formatted": format_number(v)}

    @validator("data")
    def validate_data(cls, v):
        if v == "":
            return {"default": None, "formatted": None}
        else:
            data = json.loads(v)
            return {
                "default": data,
                "formatted": json.dumps(data),
            }

    @validator("data_int")
    def validate_data_int(cls, v):
        if v == "":
            return {"default": None, "formatted": None}
        else:
            data = json.loads(v)
            if data is not None:
                data_int = [to_int(item) for item in data]
            else:
                data_int = None
            return {
                "default": data_int,
                "formatted": json.dumps(data_int),
            }


class Validator(BaseModel):
    address: str
    bonded: int
    bonded_ratio: Decimal = 0
    country: str
    cps: bool = False
    cps_sponsored_projects: int = 0
    daily_reward: Decimal = 0
    daily_reward_usd: Decimal = 0
    delegated: int
    details: str
    email: str
    grade: int
    irep: int
    irep_update_block_height: int
    last_height: int
    monthly_reward: Decimal = 0
    monthly_reward_usd: Decimal = 0
    name: str
    node_address: str
    node_status: bool = None
    p2p_endpoint: str
    penalty: int
    power: int
    productivity: Decimal = 0
    status: int
    total_blocks: int
    validated_blocks: int
    website: str

    @root_validator(pre=True)
    def root_validator(cls, values):

        cps_validators = Cps.get_cps_validators()
        # cps_sponsors_record = Cps.get_sponsors_record()

        # Set non-model variables.
        icx_usd_price = Decimal(values["icx_usd_price"])
        network_info = values["network_info"]
        total_power = Decimal(network_info["totalPower"]) / EXA
        i_global = Decimal(network_info["rewardFund"]["Iglobal"]) / EXA
        i_prep = Decimal(network_info["rewardFund"]["Iprep"]) / Decimal(100)

        for k, v in values.items():
            try:
                if v.startswith("0x"):
                    _v = to_int(v)
                    values[k] = _v
                    if k in ["bonded", "bonded", "delegated", "irep", "power"]:
                        values[k] = Decimal(_v) / EXA
            except AttributeError:
                pass

        # Set CPS participation for validator.
        if values["address"] in cps_validators:
            values["cps"] = True
        else:
            values["cps"] = False

        # if values["address"] in cps_sponsors_record.keys():
        #    values["cps_sponsored_projects"] = cps_sponsors_record[values["address"]]

        # Set bond ratio for validator.
        try:
            values["bonded_ratio"] = values["bonded"] / values["delegated"]
        except ZeroDivisionError:
            values["bonded_ratio"] = 0

        # Set productivity for validator.
        try:
            values["productivity"] = values["validated_blocks"] / values["total_blocks"]
        except ZeroDivisionError:
            values["productivity"] = 0

        # Calculate daily/monthly rewards for validator.
        try:
            monthly_reward = (
                Decimal(values["power"]) / total_power * (i_global * i_prep)
            )
            daily_reward = (Decimal(monthly_reward) * 12) / 365
            values["monthly_reward"] = monthly_reward
            values["daily_reward"] = daily_reward
            values["monthly_reward_usd"] = Decimal(monthly_reward) * icx_usd_price
            values["daily_reward_usd"] = Decimal(daily_reward) * icx_usd_price

        except Exception as e:
            print(e)

        return values

    @validator("grade")
    def validate_grade(cls, v):
        if v == 0:
            formatted = "main"
        elif v == 1:
            formatted = "sub"
        elif v == 2:
            formatted = "candidate"
        return {"default": v, "formatted": formatted}

    @validator(
        "bonded",
        "daily_reward",
        "daily_reward_usd",
        "delegated",
        "irep",
        "irep_update_block_height",
        "monthly_reward",
        "monthly_reward_usd",
        "power",
        "total_blocks",
        "validated_blocks",
    )
    def validate_number(cls, v):
        return {"default": v, "formatted": format_number(v)}

    @validator("bonded_ratio", "productivity")
    def validate_percentage(cls, v):
        return {"default": v, "formatted": format_percentage(v)}

    @validator("country")
    def validate_country(cls, v):
        return {"default": v, "formatted": CountryCodes.convert_country_code_to_hex(v)}

    @validator("name")
    def validate_name(cls, v):
        if v.startswith("Gilga Capital"):
            return "Gilga Capital"
        elif v.startswith("ICONLEO"):
            return "ICONLEO"
        elif v.startswith("ICXburners"):
            return "ICXburners"
        elif v.startswith("UNBLOCK"):
            return "UNBLOCK"
        else:
            return v


class Db_IcxSicxBnusdQuote(Document):
    id: datetime
    icx_usd: Decimal
    sicx_bnusd: Decimal
    sicx_icx: Decimal

    class Settings:
        name = "icxSicxBnusdQuotes"


# icxBlocks


class Db_IcxBlock(Document):
    id: int
    timestamp: datetime

    class Settings:
        name = "icxBlocks"
        indexes = [[("timestamp", pymongo.DESCENDING)]]


# validatorNodeUptime


class Db_ValidatorNodeStatus(Document):
    id: str  # ID is validator address (not nodeAddress)
    timestamp: datetime
    status: bool

    class Settings:
        name = "validatorNodeStatuses"
        use_cache = True
        cache_expiration_time = timedelta(seconds=600)
