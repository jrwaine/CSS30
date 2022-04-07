import json
from dataclasses import dataclass


@dataclass
class _BaseRequest:
    port: int

    def to_json(self) -> str:
        val = json.dumps({"data": self.__dict__, "data_type": self.__class__.__name__})
        return val


@dataclass
class TokenRequest(_BaseRequest):
    total_time: float


@dataclass
class TokenRequestAnswer(_BaseRequest):
    port_to: int


def load_json(msg: str) -> dict:
    dct = dict(json.loads(msg))
    return dct
