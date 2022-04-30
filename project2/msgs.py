import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class _BaseRequest:
    def to_json(self) -> str:
        val = json.dumps(self.__dict__)
        return val


@dataclass
class ResourceLiberation(_BaseRequest):
    is_liberated: bool
    resource: int


@dataclass
class ServerResp(_BaseRequest):
    msg: str
    pub_key: Optional[str]


def load_json(msg: str) -> dict:
    dct = dict(json.loads(msg))
    return dct
