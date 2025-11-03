import base64
import hashlib
from typing import Optional

from cryptography.hazmat.primitives import serialization


class CryptographyService:

    def sha256_hash(self, data: str) -> str:
        """ Compute SHA-256 hash of a string and return its hex digest. """
        return hashlib.sha256(data.encode('ascii')).hexdigest()

    def validate_signature(self, message: str, signature_b64: str, public_key_pem: str) -> bool:
        public_key_obj = serialization.load_pem_public_key(public_key_pem.encode("ascii"))

        try:
            signature = base64.b64decode(signature_b64.encode("ascii"))
            public_key_obj.verify(signature, message.encode("ascii"))
            return True
        except:
            return False

    def find_merkle_root_for_list(self, data_items: list[str]) -> Optional[str]:
        """Builds a Merkle tree and returns the root hash."""
        if not data_items:
            return None

        # If there's only one item, return its hash
        if len(data_items) == 1:
            return self.sha256_hash(data_items[0])

        # Ensure even number of items by duplicating the last if odd number of items
        if len(data_items) % 2 != 0:
            data_items.append(data_items[-1])

        # Hash and pair up the data items recursively
        next_level = []
        for i in range(0, len(data_items), 2):
            combined_hash = self.sha256_hash(data_items[i] + data_items[i + 1])
            next_level.append(combined_hash)

        # Recursively build the tree with the hashes as new leaf nodes
        return self.find_merkle_root_for_list(next_level)
