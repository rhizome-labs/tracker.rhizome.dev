from concurrent.futures import ThreadPoolExecutor

import requests
from requests.adapters import HTTPAdapter, Retry
from tracker_rhizome_dev import MAX_WORKERS
from tracker_rhizome_dev.app.icx import Icx


class Gov(Icx):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_validator_count(cls):
        validators = cls.call(cls.CHAIN_CONTRACT, "getPReps")
        validator_count = len(validators["preps"])
        return validator_count

    @classmethod
    def get_validators(cls):
        validators = cls.call(cls.CHAIN_CONTRACT, "getPReps")
        return validators

    @classmethod
    def get_validators_node_status(cls):
        def _check_node_status(
            address: str, node_endpoint: str, last_block: int
        ) -> bool:
            try:
                s = requests.Session()
                retries = Retry(
                    total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
                )
                s.mount("http://", HTTPAdapter(max_retries=retries))
                r = s.get(f"{node_endpoint}/admin/chain/0x1")
                data = r.json()
                if data["height"] >= last_block:
                    print(f"{r.status_code}: {node_endpoint}")
                    return (address, True)
                else:
                    print(f"{r.status_code}: {node_endpoint}")
                    return (address, False)
            except:
                print(f"{r.status_code}: {node_endpoint}")
                return (address, False)

        def _get_validators_node_endpoints() -> dict:
            validators_node_endpoints = {}
            url = (
                "https://icon2.mon.solidwallet.io/api/v1/items/influxdb/default?init=5"
            )
            r = requests.get(url)
            data = r.json()
            validators = data["data"]
            for validator in validators:
                if str(validator["items"]["address"]).startswith("hx"):
                    validators_node_endpoints[
                        validator["items"]["address"]
                    ] = f'http://{validator["tags"]["public_ip"]}:9000'
            return validators_node_endpoints

        # Get a dictionary that maps node addresses to public IP endpoint.
        validators_node_endpoints = _get_validators_node_endpoints()

        # Get last block from blockchain.
        last_block = cls.get_block("latest")["height"]

        # Check each address:endpoint mapping for uptime.
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(
                    _check_node_status,
                    address=address,
                    node_endpoint=node_endpoint,
                    last_block=last_block,
                )
                for address, node_endpoint in validators_node_endpoints.items()
            ]
            status_checks = [future.result() for future in futures if future.result()]

        # Create a dictionary that maps node address to validator address.
        validators = cls.get_validators()
        validators_node_address_to_validator_address = {
            validator["nodeAddress"]: validator["address"]
            for validator in validators["preps"]
        }

        # Create a dictionary that maps node address to node status.
        validators_node_status = {}
        for status in status_checks:
            validators_node_status[
                validators_node_address_to_validator_address[status[0]]
            ] = status[1]

        return validators_node_status
