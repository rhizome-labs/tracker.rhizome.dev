from time import sleep
from typing import Union

from cachetools import TTLCache, cached
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from requests.exceptions import ConnectionError

from tracker_rhizome_dev import ENV
from tracker_rhizome_dev.app.utils import to_int


class Icx:

    # Configure IconService object
    ICON_API_ENDPOINT = ENV["ICON_API_ENDPOINT"]
    ICON_SERVICE = IconService(HTTPProvider(ICON_API_ENDPOINT, 3))

    # Core Contracts
    CHAIN_CONTRACT = "cx0000000000000000000000000000000000000000"
    GOVERNANCE_CONTRACT = "cx0000000000000000000000000000000000000001"

    def __init__(self) -> None:
        self.last_block = self.get_block("latest")["height"]

    ##############
    # Primitives #
    ##############

    @classmethod
    def call(cls, to: str, method: str, params={}, height=None):
        i = 0
        while True:

            if i > 5:
                return

            try:
                call = (
                    CallBuilder()
                    .to(to)
                    .method(method)
                    .params(params)
                    .height(height)
                    .build()
                )
                result = cls.ICON_SERVICE.call(call)
                return result
            except ConnectionError as e:
                sleep(2)
                i += 1
                continue
            except KeyboardInterrupt:
                exit()

    #################
    # Stock Methods #
    #################

    @classmethod
    def get_block(
        cls, height: Union[int, str] = "latest", height_only: bool = False
    ) -> dict:
        result = cls.ICON_SERVICE.get_block(height)
        if height_only is True:
            return result["height"]
        else:
            return result

    @classmethod
    def get_score_api(cls, contract: str, height: int = None) -> dict:
        result = cls.ICON_SERVICE.get_score_api(contract, height)
        return result

    @classmethod
    def get_transaction(cls, tx_hash: str) -> dict:
        result = cls.ICON_SERVICE.get_transaction(tx_hash)
        return result

    @classmethod
    def get_transaction_result(cls, tx_hash: str) -> dict:
        result = cls.ICON_SERVICE.get_transaction_result(tx_hash)
        return result

    @classmethod
    @cached(cache=TTLCache(maxsize=1, ttl=30))
    def get_icx_usd_price(cls, height: int = None) -> float:
        result = cls.call(
            "cx087b4164a87fdfb7b714f3bafe9dfb050fd6b132",
            "get_ref_data",
            {"_symbol": "ICX"},
            height=height,
        )
        icx_usd_price = int(result["rate"], 16) / 1000000000
        return icx_usd_price

    @classmethod
    def get_network_info(cls):
        result = cls.call(cls.CHAIN_CONTRACT, "getNetworkInfo")
        for k, v in result.items():
            if isinstance(v, str):
                result[k] = to_int(v)
        for k, v in result["rewardFund"].items():
            if isinstance(v, str):
                result["rewardFund"][k] = to_int(v)
        return result

    #########
    # CALLS #
    #########

    @classmethod
    def get_irc2_token_balance(cls, token_contract: str, address: str):
        result = cls.call(token_contract, "balanceOf", params={"_owner": address})
        return result

    ########
    # IISS #
    ########

    @classmethod
    def get_icx_staking_apy(cls):
        network_info = cls.get_network_info()
        reward_fund = network_info["rewardFund"]
        voter_allocation = reward_fund["Iglobal"] * (reward_fund["Ivoter"] / 100) * 12
        total_delegated = network_info["totalDelegated"]
        icx_staking_apy = round(voter_allocation / total_delegated, 8)
        return icx_staking_apy

    @classmethod
    def get_staked_delegated_supply(cls):
        network_info = cls.get_network_info()
        staked_supply = network_info["totalStake"] / 10**18
        delegated_supply = network_info["totalDelegated"] / 10**18
        return {"delegated_supply": delegated_supply, "staked_supply": staked_supply}
