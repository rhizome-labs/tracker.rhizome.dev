import httpx
from rich import inspect


class HttpReq:
    def __init__(self) -> None:
        pass

    @classmethod
    async def get(
        cls, url: str, headers: dict = None, timeout: float = 10.0, retries=2
    ):
        try:
            async with httpx.AsyncClient(
                timeout=timeout, transport=httpx.AsyncHTTPTransport(retries=retries)
            ) as client:
                r = await client.get(url, headers=headers)
                r.raise_for_status
                return r
        except Exception as e:
            inspect(e)

    @classmethod
    async def head(cls, url: str, timeout: float = 10.0, retries=2):
        try:
            async with httpx.AsyncClient(
                timeout=timeout, transport=httpx.AsyncHTTPTransport(retries=retries)
            ) as client:
                r = await client.head(url)
                r.raise_for_status
                return r
        except Exception as e:
            inspect(e)

    @classmethod
    async def post(cls, url: str, json: dict, timeout: float = 10.0, retries=2):
        try:
            async with httpx.AsyncClient(
                timeout=timeout, transport=httpx.AsyncHTTPTransport(retries=retries)
            ) as client:
                r = await client.post(url, json=json)
                r.raise_for_status
                return r
        except Exception as e:
            inspect(e)
