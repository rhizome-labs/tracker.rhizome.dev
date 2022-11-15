from tracker_rhizome_dev.app.http_request import HttpReq


class Craft:

    CRAFT_API_URL = "https://api.craft.network"
    CRAFT_DEFAULT_COLLECTION_CONTRACT = "cx82c8c091b41413423579445032281bca5ac14fc0"

    FEATURED_COLLECTIONS = [
        ("cx82c8c091b41413423579445032281bca5ac14fc0", 897),  # Tamashi
        ("cx82c8c091b41413423579445032281bca5ac14fc0", 1461),  # Tamashi 8-Bit
        ("cx82c8c091b41413423579445032281bca5ac14fc0", 952),  # Tamashi x ICON
        ("cx82c8c091b41413423579445032281bca5ac14fc0", 1297),  # Mirai x Community
    ]

    def __init__(self) -> None:
        pass

    @classmethod
    async def get_collection(cls, collection_contract: str, collection_id: int) -> dict:
        url = f"{cls.CRAFT_API_URL}/collection/{collection_contract}:{collection_id}"
        r = await HttpReq.get(url)
        collection = r.json()
        return collection["data"]

    @classmethod
    async def get_collections(self) -> list:
        url = f"{self.CRAFT_API_URL}/collection"
        r = await HttpReq.get(url)
        collections = r.json()
        return collections["data"]

    def get_featured_collections(self) -> list:
        featured_collections = []
        for contract, id in self.FEATURED_COLLECTIONS:
            collection_info = self.get_collection(contract, id)
            print(collection_info)
            featured_collections.append(collection_info)
        return featured_collections
