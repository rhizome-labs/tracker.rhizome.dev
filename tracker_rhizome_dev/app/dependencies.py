from fastapi import HTTPException, Request, status

from tracker_rhizome_dev import ENV


async def is_htmx_request(request: Request):
    if ENV["ENV"].casefold() == "production":
        try:
            headers = dict(request.headers)
            if headers["hx-request"].casefold() == "true":
                return request
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return request


async def is_localhost_request(request: Request):
    if ENV["ENV"].casefold() == "production":
        try:
            headers = dict(request.headers)
            if headers["host"].startswith("localhost"):
                return request
            else:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    else:
        return request
