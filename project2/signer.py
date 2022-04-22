from typing import Tuple


def get_key_pair() -> Tuple[str, str]:
    ...


def sign_message(msg: str, priv_key: str) -> str:
    ...


def validate_message(msg: str, pub_key: str) -> str:
    ...
