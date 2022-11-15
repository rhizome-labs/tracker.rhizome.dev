import json
from time import sleep

import requests


def main():
    validators_dict = {}
    url = f"https://main.tracker.solidwallet.io/v3/iiss/prep/list?count=500"
    r = requests.get(url)
    data = r.json()
    validators = data["data"]
    for validator in validators:
        validators_dict[validator["address"]] = validator["name"]

    print(json.dumps(validators_dict, indent=4))


if __name__ == "__main__":
    main()
