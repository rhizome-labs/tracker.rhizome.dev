import json
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from functools import lru_cache

from cachetools import LRUCache, cached
from fastapi import Query
from iconsdk.exception import JSONRPCException

from tracker_rhizome_dev import EXA, MAX_WORKERS
from tracker_rhizome_dev.app.data.tokens import Tokens
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.models.balanced import (
    BalancedLoan,
    Db_BalancedPoolDynamicData,
    Db_BalancedPoolStaticData,
)
from tracker_rhizome_dev.app.tracker import Tracker
from tracker_rhizome_dev.app.utils import to_int


class Balanced(Icx):

    BALANCED_DEX_CONTRACT = "cxa0af3165c08318e988cb30993b3048335b94af6c"
    BALANCED_LOANS_CONTRACT = "cx66d4d90f5f113eba575bf793570135f9b10cece1"
    BNUSD_CONTRACT = "cx88fd7df7ddff82f7cc735c871dc519838cb235bb"
    SICX_CONTRACT = "cx2609b924e33ef00b648a409245c7ea394c467824"
    FEATURED_POOL_IDS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 17, 31]

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_borrower_count(cls):
        result = cls.call(cls.BALANCED_LOANS_CONTRACT, "borrowerCount")
        return to_int(result)

    @classmethod
    def get_nonzero_positions(cls):
        result = cls.call(cls.BALANCED_LOANS_CONTRACT, "getNonzeroPositionCount")
        return to_int(result)

    @classmethod
    async def get_liquidations(
        self,
        page: int = 1,
        limit: int = 100,
    ):
        skip = int((page - 1) * limit)
        liquidations = await Tracker.get_logs(
            self.BALANCED_LOANS_CONTRACT, "Liquidate", limit, skip
        )
        return liquidations

    def get_pool(self, pool_id: int, height: int = None):
        """
        Returns Balanced pool stats for the provided pool_id.

        Args:
            pool_id (int): The ID number of a pool on Balanced.
            height (int): The block height to query.

        Returns:
            A dictionary containing stats for the pool.
        """
        # Query for pool data at provided block height (latest block by default).
        pool = self._get_pool(pool_id, height)

        # Continue if pool is not 'None'.
        if pool is not None:
            # Query for pool data 24 hours (43,200 blocks) prior to the provided 'height'.
            pool_24h_ago = self._get_pool(pool_id, height=self.last_block - 43200)
            try:
                # Set 24h change to 0 for sICX/ICX pool.
                if pool_id == 1:
                    pool["price_daily_change_amount"] = 0
                    pool["price_daily_change_percent"] = 0
                    pool["base_daily_change_amount"] = 0
                    pool["base_daily_change_percent"] = 0
                else:
                    # Calculate the price change amount and percentage in the last 24 hours.
                    price_daily_change_amount = pool["price"] - pool_24h_ago["price"]
                    price_daily_change_percent = (
                        price_daily_change_amount / pool_24h_ago["price"]
                    )
                    pool["price_daily_change_amount"] = price_daily_change_amount
                    pool["price_daily_change_percent"] = price_daily_change_percent
            except:
                # Set both to 0 if there's an issue (probably because the pool didn't exist 24 hours ago).
                pool["price_daily_change_amount"] = 0
                pool["price_daily_change_percent"] = 0
            return pool
        # Return 'None' if pool is 'None'.
        else:
            return None

    def get_pool_dynamic_metadata(
        self, pool_id: int, height: int = None
    ) -> Db_BalancedPoolDynamicData:
        result = self.get_pool(pool_id, height)
        if result is not None:
            return Db_BalancedPoolDynamicData(**result)
        else:
            return None

    def get_pool_static_metadata(self, pool_id: int, height: int = None):
        result = self.get_pool(pool_id, height)
        return Db_BalancedPoolStaticData(**result)

    def get_pools(self, height: int = None):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.get_pool, pool_id=id, height=height)
                for id in range(1, self.get_pool_count())
            ]
            pools = [future.result() for future in futures if future.result()]
        return sorted(pools, key=lambda k: k["id"])

    def get_pool_count(self, height: int = None):
        result = self.call(self.BALANCED_DEX_CONTRACT, "getNonce")
        return to_int(result)

    @lru_cache(maxsize=10000)
    def get_loan_address(self, index: int, height: int):
        try:
            with open(f"./tracker_rhizome_dev/app/cache/balanced-loans.json", "r") as f:
                data = json.load(f)
                result = data[str(index)]
                return result
        # If cache file is not found, make a request to the blockchain to get the position address.
        except (FileNotFoundError, KeyError):
            result = self.call(
                self.BALANCED_LOANS_CONTRACT, "getPositionAddress", {"_index": index}
            )
            return result

    def get_loan(self, index: int, height: int = None):
        loan_address = self.get_loan_address(index, height)
        try:
            loan = self.call(
                self.BALANCED_LOANS_CONTRACT,
                "getAccountPositions",
                {"_owner": loan_address},
            )
            loan = BalancedLoan(**loan)
            print(f"Processing Balanced Loan #{index}...")
            return loan
        except JSONRPCException:
            return None

    def get_loans(self, height: int = None, dump: bool = True):
        loan_count = self.get_borrower_count()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.get_loan, index=i) for i in range(1, loan_count)
            ]
            loans = [future.result() for future in futures]
            loans = [loan for loan in loans if loan is not None]
        if dump is True:
            loan_index_address_map = {str(loan.pos_id): loan.address for loan in loans}
            with open(
                f"./tracker_rhizome_dev/app/cache/balanced-loans.json", "w+"
            ) as f:
                f.write(json.dumps(loan_index_address_map, indent=4))
        return loans

    def get_price_by_name(self, pool_name: str):
        quote = self.call(
            self.BALANCED_DEX_CONTRACT, "getPriceByName", {"_name": pool_name}
        )
        return quote

    @classmethod
    def get_stability_fund(cls) -> list:
        usds_balance = cls.get_irc2_token_balance(
            "cxbb2871f468a3008f80b08fdde5b8b951583acf06",
            "cxa09dbb60dcb62fffbd232b6eae132d730a2aafa6",
        )
        iusdc_balance = cls.get_irc2_token_balance(
            "cxae3034235540b924dfcc1b45836c293dcc82bfb7",
            "cxa09dbb60dcb62fffbd232b6eae132d730a2aafa6",
        )
        return [
            ("IUSDC", Decimal(to_int(iusdc_balance)) / Decimal(10**6)),
            ("USDS", Decimal(to_int(usds_balance)) / Decimal(10**18)),
        ]

    @classmethod
    def get_loan_collateral(cls) -> Decimal:
        params = {"_owner": cls.BALANCED_LOANS_CONTRACT}
        result = cls.call(cls.SICX_CONTRACT, "balanceOf", params)
        return Decimal(to_int(result)) / EXA

    @classmethod
    def get_total_debt(cls) -> Decimal:
        result = cls.call(cls.BNUSD_CONTRACT, "totalSupply")
        return Decimal(to_int(result)) / EXA

    def _get_pool(self, pool_id: int, height: int = None) -> list:
        try:
            result = self.call(
                self.BALANCED_DEX_CONTRACT,
                "getPoolStats",
                {"_id": pool_id},
                height=height,
            )
            result["id"] = pool_id
            base_dec = to_int(result["base_decimals"])
            quote_dec = to_int(result["quote_decimals"])
            base_name = Tokens.get_token_name(result["base_token"])
            quote_name = Tokens.get_token_name(result["quote_token"])
            base_symbol = Tokens.get_token_symbol(result["base_token"])
            quote_symbol = Tokens.get_token_symbol(result["quote_token"])
            precision = int((quote_dec - base_dec) + 18)
            result["base_decimals"] = base_dec
            result["quote_decimals"] = quote_dec
            result["precision"] = precision
            result["base"] = Decimal(to_int(result["base"])) / Decimal(10**base_dec)
            result["quote"] = Decimal(to_int(result["quote"])) / Decimal(
                10**quote_dec
            )
            result["base_name"] = base_name
            result["quote_name"] = quote_name
            result["base_symbol"] = base_symbol
            result["quote_symbol"] = quote_symbol
            result["pool_name"] = f"{base_symbol}/{quote_symbol}"
            result["min_quote"] = Decimal(to_int(result["min_quote"])) / Decimal(
                10**quote_dec
            )
            result["price"] = Decimal(to_int(result["price"])) / Decimal(
                10**precision
            )
            result["total_supply"] = Decimal(to_int(result["total_supply"])) / Decimal(
                10**quote_dec
            )
            return result
        except JSONRPCException as e:
            if e.code == -30006:  # Pool doesn't exist at the specified block height.
                return None
