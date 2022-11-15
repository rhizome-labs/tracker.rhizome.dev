import json
from time import sleep

import requests


def main():
    contract_dict = {}
    page = 1
    while True:
        url = f"https://main.tracker.solidwallet.io/v3/contract/list?page={page}&count=100"
        r = requests.get(url)
        data = r.json()
        contracts = data["data"]
        print(contracts)
        if len(contracts) > 0:
            for contract in contracts:
                if (
                    contract["contractName"] is not None
                    and contract["contractName"] != "-"
                ):
                    contract_dict[contract["address"]] = contract["contractName"]
        else:
            break
        page += 1

    print(json.dumps(contract_dict, indent=4))


if __name__ == "__main__":
    main()
