class AuthenticatorSigner:
    def __init__(self, pub_key: int, priv_key: int) -> None:
        pass

    def sign_doc_w_public(self, doc_sign: str) -> str:
        pass

    def decode_doc_w_private(self, doc_signed: str) -> str:
        pass
