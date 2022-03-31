import json
from dataclasses import dataclass


@dataclass
class _BaseRequest:
    port: int

    def to_json(self) -> str:
        return json.dumps({"data": self.asdict(), "class": self.__name__})


@dataclass
class TokenRequest(_BaseRequest):
    total_time: float


@dataclass
class TokenRequestAnswer(_BaseRequest):
    port_to: int


@dataclass
class PublicKeyRequest(_BaseRequest):
    ...


@dataclass
class PublicKeyAnswer(_BaseRequest):
    public_key: str


def load_json(msg: str) -> dict:
    dct = dict(json.loads(msg))
    return dct
