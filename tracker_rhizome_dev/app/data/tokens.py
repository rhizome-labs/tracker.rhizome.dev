from tracker_rhizome_dev.app.icx import Icx


class Tokens(Icx):
    def __init__(self) -> None:
        super().__init__()

    TOKEN_METADATA = {
        "cx3fd4769e413657304d4928b95b88fd6eb53f9a8b": {
            "symbol": "IDOGE",
            "name": "iDoge",
            "decimals": 18,
        },
        "cx2609b924e33ef00b648a409245c7ea394c467824": {
            "symbol": "sICX",
            "name": "Staked ICX",
            "decimals": 18,
        },
        "cxf61cd5a45dc9f91c15aa65831a30a90d59a09619": {
            "symbol": "BALN",
            "name": "Balance Token",
            "decimals": 18,
        },
        "cx77d798a899a5103c2d389c5ba04a4cfa624425ba": {
            "symbol": "CHKN",
            "name": "Chicken",
            "decimals": 18,
        },
        "cx785d504f44b5d2c8dac04c5a1ecd75f18ee57d16": {
            "symbol": "FIN",
            "name": "Finance Token",
            "decimals": 18,
        },
        "cx66f2ed0663d5aa7efe92ab41b1e0e19ac73007a4": {
            "symbol": "LDX",
            "name": "LambdaX",
            "decimals": 18,
        },
        "cxbb2871f468a3008f80b08fdde5b8b951583acf06": {
            "symbol": "USDS",
            "name": "Stably USD",
            "decimals": 18,
        },
        "cxe7c05b43b3832c04735e7f109409ebcb9c19e664": {
            "symbol": "IAM",
            "name": "IAM Token",
            "decimals": 18,
        },
        "cxcf5424ca2acae98db83ee5a6a5fe8e8575474167": {
            "symbol": "CODA",
            "name": "Coda Governance Token",
            "decimals": 18,
        },
        "cx924b9d3acf963bf7ae82cd45cd84c4b3484f8b1f": {
            "symbol": "IETH",
            "name": "ICON Ethereum",
            "decimals": 18,
        },
        "cxc0b5b52c9f8b4251a47e91dda3bd61e5512cd782": {
            "symbol": "TAP",
            "name": "TapToken",
            "decimals": 18,
        },
        "cx6139a27c15f1653471ffba0b4b88dc15de7e3267": {
            "symbol": "GBET",
            "name": "GangstaBet Token",
            "decimals": 18,
        },
        "cx3a36ea1f6b9aa3d2dd9cb68e8987bcc3aabaaa88": {
            "symbol": "IUSDT",
            "name": "ICON Tether",
            "decimals": 6,
        },
        "cx2e6d0fc0eca04965d06038c8406093337f085fcf": {
            "symbol": "CFT",
            "name": "Craft",
            "decimals": 18,
        },
        "cx1a29259a59f463a67bb2ef84398b30ca56b5830a": {
            "symbol": "OMM",
            "name": "Omm Token",
            "decimals": 18,
        },
        "cx369a5f4ce4f4648dfc96ba0c8229be0693b4eca2": {
            "symbol": "METX",
            "name": "Metanyx",
            "decimals": 18,
        },
        "cxae3034235540b924dfcc1b45836c293dcc82bfb7": {
            "symbol": "IUSDC",
            "name": "ICON USD Coin",
            "decimals": 6,
        },
        "cx88fd7df7ddff82f7cc735c871dc519838cb235bb": {
            "symbol": "bnUSD",
            "name": "Balanced Dollar",
            "decimals": 18,
        },
        "cx1aee86144612387ef8f9c11dccad4ba578dd42ed": {
            "symbol": "NOTMIRAI",
            "name": "Not Mirai Token",
            "decimals": 18,
        },
        "cx13b52d9f24db8d64d93a31926e3c69d44fbe8f9a": {
            "symbol": "CLAW",
            "name": "Claw",
            "decimals": 18,
        },
        "cx0bb718a35e7fc8faffe6faf82b32f6f7cb5e7c81": {
            "symbol": "CHIU",
            "name": "Chihua Inu",
            "decimals": 18,
        },
    }

    def __init__(self) -> None:
        pass

    @classmethod
    def get_token_decimals(cls, contract: str) -> str:
        if contract is None:
            return "ICX"
        else:
            try:
                return cls.TOKEN_METADATA[contract]["decimals"]
            except:
                try:
                    decimals = cls.call(contract, "decimals")
                    return decimals
                except:
                    return "NULL"

    @classmethod
    def get_token_name(cls, contract: str) -> str:
        if contract is None:
            return "ICX"
        else:
            try:
                return cls.TOKEN_METADATA[contract]["name"]
            except:
                try:
                    token_name = cls.call(contract, "name")
                    return token_name
                except:
                    return "NULL"

    @classmethod
    def get_token_symbol(cls, contract: str) -> str:
        if contract is None:
            return "ICX"
        else:
            try:
                return cls.TOKEN_METADATA[contract]["symbol"]
            except:
                try:
                    token_symbol = cls.call(contract, "symbol")
                    return token_symbol
                except:
                    return "NULL"
