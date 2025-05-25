import hashlib
import json
from typing import Tuple
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import base58
import os

class Wallet:
    def __init__(self, private_key: str = None):
        if private_key:
            self.private_key = SigningKey.from_string(
                base58.b58decode(private_key),
                curve=SECP256k1
            )
        else:
            self.private_key = SigningKey.generate(curve=SECP256k1)
        
        self.public_key = self.private_key.get_verifying_key()
        self.address = self.generate_address()

    def generate_address(self) -> str:
        # Convert public key to bytes
        public_key_bytes = self.public_key.to_string()
        # Hash the public key
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        # Add version byte and checksum
        version_byte = b'\x00'  # Main network version byte
        payload = version_byte + sha256_hash
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        address_bytes = payload + checksum
        # Base58 encode
        return base58.b58encode(address_bytes).decode('utf-8')

    def get_private_key(self) -> str:
        return base58.b58encode(self.private_key.to_string()).decode('utf-8')

    def get_public_key(self) -> str:
        return base58.b58encode(self.public_key.to_string()).decode('utf-8')

    def save_to_file(self, filename: str) -> None:
        wallet_data = {
            "private_key": self.get_private_key(),
            "public_key": self.get_public_key(),
            "address": self.address
        }
        with open(filename, 'w') as f:
            json.dump(wallet_data, f, indent=4)

    @classmethod
    def load_from_file(cls, filename: str) -> 'Wallet':
        with open(filename, 'r') as f:
            wallet_data = json.load(f)
        return cls(private_key=wallet_data["private_key"])

    def sign_transaction(self, transaction_data: dict) -> str:
        transaction_string = json.dumps(transaction_data, sort_keys=True)
        signature = self.private_key.sign(transaction_string.encode())
        return base58.b58encode(signature).decode('utf-8')

    def verify_transaction(self, transaction_data: dict, signature: str) -> bool:
        try:
            transaction_string = json.dumps(transaction_data, sort_keys=True)
            signature_bytes = base58.b58decode(signature)
            return self.public_key.verify(signature_bytes, transaction_string.encode())
        except:
            return False

    def get_balance(self, blockchain) -> float:
        balance = 0.0
        for block in blockchain.chain:
            for transaction in block.transactions:
                if transaction["recipient"] == self.address:
                    balance += transaction["amount"]
                if transaction["sender"] == self.address:
                    balance -= transaction["amount"]
        return balance 