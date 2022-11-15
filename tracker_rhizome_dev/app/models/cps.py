from decimal import Decimal
from typing import Union

from pydantic import BaseModel, validator
from tracker_rhizome_dev import EXA
from tracker_rhizome_dev.app.utils import to_int


class CpsValidator(BaseModel):
    address: str
    delegated: Union[str, None]
    name: Union[str, None]

    @validator("delegated")
    def validate_delegated(cls, v):
        if v is None:
            return 0
        else:
            v = Decimal(to_int(v)) / EXA
            return v
