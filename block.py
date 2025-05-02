import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], 
                 timestamp: float = None, previous_hash: str = None, 
                 nonce: int = 0):
        self.index = index
        self.timestamp = timestamp or datetime.now().timestamp()
        self.transactions = transactions
        self.previous_hash = previous_hash or "0" * 64
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }

    @classmethod
    def from_dict(cls, block_dict: Dict[str, Any]) -> 'Block':
        block = cls(
            index=block_dict["index"],
            transactions=block_dict["transactions"],
            timestamp=block_dict["timestamp"],
            previous_hash=block_dict["previous_hash"],
            nonce=block_dict["nonce"]
        )
        block.hash = block_dict["hash"]
        return block 