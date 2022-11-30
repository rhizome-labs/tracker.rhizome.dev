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
    async def get_address_transactions(
        cls,
        address: str,
        limit: int = 25,
        skip: int = 0,
        format: bool = True,
    ):
        url = f"{cls.ICON_TRACKER_ENDPOINT}/transactions/address/{ address }/?limit={limit}&skip={skip}"
        r = await HttpReq.get(url)
        transactions = r.json()

        if format is True:
            transactions = [Transaction(**transaction) for transaction in transactions]
            return transactions
        else:
            return transactions

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
        from_address: str = None,
        to_address: str = None,
        type: str = "transaction",
        block_height: int = None,
        start_block_height: int = None,
        end_block_height: int = None,
        method: str = None,
        limit: int = 25,
        skip: int = 0,
        sort: str = "desc",
        format: bool = True,
    ) -> list:

        # Build query string for origin address.
        if from_address is None:
            from_address_str = ""
        else:
            from_address_str = f"&from={from_address}"

        # Build query string for destination address.
        if to_address is None:
            to_address_str = ""
        else:
            to_address_str = f"&to={to_address}"

        # Build query string for block height.
        if block_height is None:
            block_height_str = ""
        else:
            block_height_str = f"&block_number={block_height}"

        # Build query string for start block height.
        if start_block_height is None:
            start_block_height_str = ""
        else:
            start_block_height_str = f"&start_block_number={start_block_height}"

        # Build query string for end block height.
        if end_block_height is None:
            end_block_height_str = ""
        else:
            end_block_height_str = f"&end_block_number={end_block_height}"

        # Build query string for method.
        if method is None:
            method_str = ""
        else:
            method_str = f"&method={method}"

        url = f"{cls.ICON_TRACKER_ENDPOINT}/transactions?limit={limit}&skip={skip}&sort={sort}&type={type}{from_address_str}{to_address_str}{block_height_str}{start_block_height_str}{end_block_height_str}{method_str}"
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
