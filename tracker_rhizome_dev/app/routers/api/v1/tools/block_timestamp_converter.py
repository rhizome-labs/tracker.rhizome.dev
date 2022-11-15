from fastapi import APIRouter, Request, Response, status
from fastapi.exceptions import HTTPException

router = APIRouter(prefix="/block-timestamp-converter")


@router.get("/")
async def get_block_timestamp_converter():
    return
