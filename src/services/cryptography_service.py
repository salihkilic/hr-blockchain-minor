import base64
import hashlib

from cryptography.hazmat.primitives import serialization


class CryptographyService:

    def cryptographic_hash(self, data: str) -> str:
        return hashlib.sha256(data.encode('ascii')).hexdigest()

    def validate_signature(self, message: str, signature_b64: str, public_key_pem: str) -> bool:
        public_key_obj = serialization.load_pem_public_key(public_key_pem.encode("ascii"))

        try:
            signature = base64.b64decode(signature_b64.encode("ascii"))
            public_key_obj.verify(signature, message.encode("ascii"))
            return True
        except:
            return False