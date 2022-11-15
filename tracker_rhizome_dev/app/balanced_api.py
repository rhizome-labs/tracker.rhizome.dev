from decimal import Decimal

from tracker_rhizome_dev.app.data.tokens import Tokens
from tracker_rhizome_dev.app.http_request import HttpReq
from tracker_rhizome_dev.app.utils import to_int


class BalancedApi:

    BALANCED_API_URL = "https://balanced.sudoblock.io/api/v1"

    def __init__(self) -> None:
        pass

    @classmethod
    async def get_borrower_count(cls):
        r = await HttpReq.get(f"{cls.BALANCED_API_URL}/stats/num-borrowers")
        data = r.json()
        borrower_count = int(data["num_borrowers"], 16)
        return borrower_count

    @classmethod
    async def get_daofund_balanced_sheet(cls):
        r = await HttpReq.get(
            f"{cls.BALANCED_API_URL}/stats/daofund-balance-sheet?timestamp=-1"
        )
        data = r.json()
        balance_sheet = []
        for contract, amount in data.items():
            balance_sheet.append(
                {
                    "symbol": Tokens.get_token_symbol(contract),
                    "amount": int(amount, 16)
                    / 10 ** Tokens.get_token_decimals(contract),
                }
            )
        return balance_sheet

    @classmethod
    async def get_24h_exchange_volume(cls):
        r = await HttpReq.get(f"{cls.BALANCED_API_URL}/stats/exchange-volume-24h")
        data = r.json()
        for volume_details in data.values():
            for side, volume in volume_details.items():
                volume_details[side] = int(volume, 16)
        return data

    @classmethod
    async def get_total_transactions(cls):
        r = await HttpReq.get(f"{cls.BALANCED_API_URL}/stats/total-transactions")
        data = r.json()
        return data

    @classmethod
    async def get_total_value_locked(cls):
        r = await HttpReq.get(f"{cls.BALANCED_API_URL}/stats/total-value-locked")
        data = r.json()
        data["total_value_locked_usd"] = Decimal(
            to_int(data["total_value_locked_usd"])
        ) / Decimal(10**18)
        data["dex_value_locked_usd"] = Decimal(
            to_int(data["dex_value_locked_usd"])
        ) / Decimal(10**18)
        data["loans_value_locked_usd"] = Decimal(
            to_int(data["loans_value_locked_usd"])
        ) / Decimal(10**18)
        return data
