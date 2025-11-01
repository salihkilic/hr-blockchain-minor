import hashlib


class CryptographyService:

    def cryptographic_hash(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()