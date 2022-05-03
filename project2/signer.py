import time
from typing import Tuple

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


def get_key_pair() -> Tuple[str, str]:
    key = RSA.generate(1024)
    pub_key = key.public_key().export_key("PEM")
    priv_key = key.export_key("PEM")
    return pub_key.decode("utf-8"), priv_key.decode("utf-8")


def sign_message(msg: str, priv_key: str) -> str:
    # t0 = time.time()
    private_key = RSA.import_key(priv_key)
    rsa_private_key = PKCS1_v1_5.new(private_key)
    msg_hash = SHA256.new(msg.encode("utf-8"))
    signed_text: bytes = rsa_private_key.sign(msg_hash)
    # print("sign total", time.time()-t0)
    return signed_text.hex()


def validate_message(msg: str, pub_key: str, signature: str):
    public_key = RSA.import_key(pub_key)
    rsa_public_key = PKCS1_v1_5.new(public_key)
    msg_hash = SHA256.new(msg.encode("utf-8"))
    rsa_public_key.verify(msg_hash, bytes.fromhex(signature))
