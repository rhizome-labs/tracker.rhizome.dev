class CountryCodes:
    def __init__(self) -> None:
        pass

    @classmethod
    def convert_country_code_to_hex(cls, country_code: str) -> str:
        """
        Returns a hexadecimal HTML entity for a country code.
        """
        COUNTRY_CODE_TO_HEX = {
            "AUS": "&#127462&#127482",
            "BEL": "&#127463&#127466",
            "CAN": "&#127464&#127462",
            "CHE": "&#127464&#127469",
            "CYM": "&#127472&#127486",
            "CZE": "&#127464&#127487",
            "DEU": "&#127465&#127466",
            "FRA": "&#127467&#127479",
            "GBR": "&#127468&#127463",
            "HRV": "&#127469&#127479",
            "IND": "&#127470&#127475",
            "JPN": "&#127471&#127477",
            "KOR": "&#127472&#127479",
            "NLD": "&#127475&#127473",
            "NZL": "&#127475&#127487",
            "PHL": "&#127477&#127469",
            "SGP": "&#127480&#127468",
            "SVN": "&#127480&#127470",
            "THA": "&#127481&#127469",
            "UKR": "&#127482&#127462",
            "USA": "&#127482&#127480",
            "ZAF": "&#127487&#127462",
        }
        if country_code in COUNTRY_CODE_TO_HEX:
            return COUNTRY_CODE_TO_HEX[country_code]
        else:
            return ""
