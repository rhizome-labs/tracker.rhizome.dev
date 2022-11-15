from json.decoder import JSONDecodeError

from tracker_rhizome_dev import ENV
from tracker_rhizome_dev.app.http_request import HttpReq
from tracker_rhizome_dev.app.models.icx import (
    Block,
    Contract,
    Log,
    TokenTransfer,
    Transaction,
    TransactionDetail,
    TransactionLog,
    Validator,
)


class Tracker:

    ICON_TRACKER_ENDPOINT = ENV["ICON_TRACKER_ENDPOINT"]

    def __init__(self) -> None:
        pass

    @classmethod
    async def get_address_details(cls, address: str):
        url = f"https://tracker.icon.community/api/v1/addresses/details/{ address }/"
        r = await HttpReq.get(url)
        data = r.json()
        return data

    @classmethod
    async def get_block_from_timestamp(cls, timestamp: int) -> int:
        """
        Returns block height for the provided timestamp.

        Args:
            timestamp (int): Unix timestamp in seconds (must be greater than 1516819217)

        Returns:
            int: Block height for the provided timestamp.
        """
        url = f"{cls.ICON_TRACKER_ENDPOINT}/blocks/timestamp/{timestamp * 1000000}/"  # Convert timestamp from s to ms.
        r = await HttpReq.get(url)
        data = r.json()
        return data["number"]

    @classmethod
    async def get_blocks(
        cls,
        limit: int = 100,
        sort: str = "desc",
        format: bool = True,
    ) -> list:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/blocks?limit={limit}&sort={sort}"
        r = await HttpReq.get(url)
        data = r.json()
        if format is True:
            blocks = [Block(**block) for block in data]
            return blocks
        else:
            return data

    @classmethod
    async def get_contracts(
        cls, limit: int = 100, skip: int = 0, token_standard: str = None
    ):
        if token_standard is None:
            url = f"{cls.ICON_TRACKER_ENDPOINT}/addresses/contracts?limit={limit}&skip={skip}"
        else:
            url = f"{cls.ICON_TRACKER_ENDPOINT}/addresses/contracts?limit={limit}&skip={skip}&token_standard={token_standard}"
        r = await HttpReq.get(url)
        data = r.json()
        contracts = [Contract(**contract) for contract in data]
        return contracts

    @classmethod
    async def get_logs(cls, address: str, method: str, limit: int = 100, skip: int = 0):
        url = f"{cls.ICON_TRACKER_ENDPOINT}/logs/?limit={limit}&skip={skip}&address={address}&method={method}"
        r = await HttpReq.get(url)
        data = r.json()
        logs = [Log(**log) for log in data]
        return logs

    @classmethod
    async def get_market_cap(cls):
        url = "https://main.tracker.solidwallet.io/v3/main/mainInfo"
        r = await HttpReq.get(url)
        data = r.json()
        market_cap = data["tmainInfo"]["marketCap"]
        return market_cap

    @classmethod
    async def get_token_transfers(
        cls, limit: int = 25, skip: int = 0, sort: str = "desc"
    ) -> list:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/transactions/token-transfers?limit={limit}&skip={skip}&sort={sort}&type=transaction"
        r = await HttpReq.get(url)
        data = r.json()
        token_transfers = [TokenTransfer(**token_transfer) for token_transfer in data]
        return int(token_transfers)

    @classmethod
    async def get_total_token_transfers(cls) -> int:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/transactions/token-transfers"
        r = await HttpReq.head(url)
        token_transfers = r.headers["x-total-count"]
        return int(token_transfers)

    @classmethod
    async def get_total_transactions(cls) -> int:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/transactions"
        r = await HttpReq.head(url)
        total_transactions = r.headers["x-total-count"]
        return int(total_transactions)

    @classmethod
    async def get_transaction_details(cls, tx_hash: str) -> TransactionDetail:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/transactions/details/{tx_hash}"
        r = await HttpReq.get(url)
        data = r.json()
        transaction = TransactionDetail(**data)
        return transaction

    @classmethod
    async def get_transaction_logs(cls, tx_hash: str):
        url = f"{cls.ICON_TRACKER_ENDPOINT}/logs?transaction_hash={tx_hash}"
        r = await HttpReq.get(url)
        try:
            data = r.json()
            logs = [TransactionLog(**log) for log in data]
            return sorted(logs, key=lambda k: k.log_index)
        except JSONDecodeError:
            return None

    @classmethod
    async def get_transactions(
        cls,
        limit: int = 25,
        skip: int = 0,
        sort: str = "desc",
        format: bool = True,
    ) -> list:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/transactions?limit={limit}&skip={skip}&sort={sort}&type=transaction"
        r = await HttpReq.get(url)
        data = r.json()
        if format is True:
            transactions = [Transaction(**transaction) for transaction in data]
            return transactions
        else:
            return data

    @classmethod
    async def get_validators(cls) -> list:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/governance/preps"
        r = await HttpReq.get(url)
        data = r.json()
        validators = [Validator(**validator) for validator in data]
        return sorted(validators, key=lambda k: k.power, reverse=True)

    @classmethod
    async def get_total_validators(cls) -> list:
        url = f"{cls.ICON_TRACKER_ENDPOINT}/governance/preps"
        r = await HttpReq.get(url)
        data = r.json()
        validators = [Validator(**validator) for validator in data]
        return len(validators)
