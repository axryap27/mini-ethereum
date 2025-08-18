import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import base58

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, 
                 signature: str = None, timestamp: float = None,
                 gas_limit: int = 21000, gas_price: float = 0.001,
                 nonce: int = 0, data: str = ""):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or datetime.now().timestamp()
        self.signature = signature
        self.gas_limit = gas_limit
        self.gas_price = gas_price
        self.gas_fee = gas_limit * gas_price
        self.nonce = nonce
        self.data = data
        self.gas_used = 21000
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        transaction_string = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "gas_limit": self.gas_limit,
            "gas_price": self.gas_price,
            "nonce": self.nonce,
            "data": self.data
        }, sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, private_key: SigningKey) -> None:
        if self.signature:
            raise ValueError("Transaction already signed")
        
        transaction_data = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "gas_limit": self.gas_limit,
            "gas_price": self.gas_price,
            "nonce": self.nonce,
            "data": self.data
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
                "timestamp": self.timestamp,
                "gas_limit": self.gas_limit,
                "gas_price": self.gas_price,
                "nonce": self.nonce,
                "data": self.data
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
            "hash": self.hash,
            "gas_limit": self.gas_limit,
            "gas_price": self.gas_price,
            "gas_fee": self.gas_fee,
            "gas_used": self.gas_used,
            "nonce": self.nonce,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, transaction_dict: Dict[str, Any]) -> 'Transaction':
        transaction = cls(
            sender=transaction_dict["sender"],
            recipient=transaction_dict["recipient"],
            amount=transaction_dict["amount"],
            timestamp=transaction_dict["timestamp"],
            signature=transaction_dict.get("signature"),
            gas_limit=transaction_dict.get("gas_limit", 21000),
            gas_price=transaction_dict.get("gas_price", 0.001),
            nonce=transaction_dict.get("nonce", 0),
            data=transaction_dict.get("data", "")
        )
        transaction.hash = transaction_dict.get("hash", transaction.compute_hash())
        transaction.gas_used = transaction_dict.get("gas_used", 21000)
        return transaction

    def is_valid(self) -> bool:
        if self.amount < 0:
            return False
        if not self.sender or not self.recipient:
            return False
        if self.gas_limit <= 0 or self.gas_price < 0:
            return False
        if self.hash != self.compute_hash():
            return False
        return True

    def execute(self, blockchain) -> bool:
        if not self.is_valid():
            return False
        
        if self.data:
            self.gas_used = min(self.gas_limit, 50000)
        else:
            self.gas_used = 21000
            
        return True 