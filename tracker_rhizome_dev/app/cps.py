from cachetools import TTLCache, cached
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.utils import to_int


class Cps(Icx):

    CPS_CONTRACT = "cx9f4ab72f854d3ccdc59aa6f2c3e2215dd62e879f"

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    @cached(cache=TTLCache(maxsize=1, ttl=3600))
    def get_cps_validators(cls, format: bool = True) -> list:
        result = cls.call(cls.CPS_CONTRACT, "get_PReps")
        validators = [validator["address"] for validator in result]
        return validators


#    @classmethod
#    @cached(cache=TTLCache(maxsize=1, ttl=3600))
#    def get_sponsors_record(cls) -> dict:
#        result = cls.call(cls.CPS_CONTRACT, "get_sponsors_record")
#        for k, v in result.items():
#            result[k] = to_int(v)
#        return result
