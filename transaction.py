import hashlib
import json
from typing import Dict, Any
from datetime import datetime
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import base58

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, 
                 signature: str = None, timestamp: float = None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or datetime.now().timestamp()
        self.signature = signature
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        transaction_string = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, private_key: SigningKey) -> None:
        if self.signature:
            raise ValueError("Transaction already signed")
        
        transaction_data = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp
        }
        transaction_string = json.dumps(transaction_data, sort_keys=True)
        signature = private_key.sign(transaction_string.encode())
        self.signature = base58.b58encode(signature).decode('utf-8')

    def verify_signature(self) -> bool:
        if not self.signature:
            return False
        
        try:
            public_key = VerifyingKey.from_string(
                base58.b58decode(self.sender),
                curve=SECP256k1
            )
            transaction_data = {
                "sender": self.sender,
                "recipient": self.recipient,
                "amount": self.amount,
                "timestamp": self.timestamp
            }
            transaction_string = json.dumps(transaction_data, sort_keys=True)
            signature = base58.b58decode(self.signature)
            return public_key.verify(signature, transaction_string.encode())
        except:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, transaction_dict: Dict[str, Any]) -> 'Transaction':
        transaction = cls(
            sender=transaction_dict["sender"],
            recipient=transaction_dict["recipient"],
            amount=transaction_dict["amount"],
            timestamp=transaction_dict["timestamp"],
            signature=transaction_dict["signature"]
        )
        transaction.hash = transaction_dict["hash"]
        return transaction

    def is_valid(self) -> bool:
        # Basic validation
        if self.amount <= 0:
            return False
        if not self.sender or not self.recipient:
            return False
        if self.hash != self.compute_hash():
            return False
        return True 