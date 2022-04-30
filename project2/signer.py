from typing import Tuple


def get_key_pair() -> Tuple[str, str]:
    return "a", "b"


def sign_message(msg: str, priv_key: str) -> str:
    # TODO
    return msg


def validate_message(msg: str, pub_key: str) -> str:
    # TODO
    return msg
