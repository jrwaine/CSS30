from typing import Tuple
from Crypto.PublicKey import RSA


def get_key_pair() -> Tuple[str, str]:
    key = RSA.generate(2048)
    return "a", "b"


def sign_message(msg: str, priv_key: str) -> str:
    # TODO
    return msg


def validate_message(msg: str, pub_key: str) -> str:
    # TODO
    return msg
