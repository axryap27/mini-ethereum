import json
from typing import List, Dict, Any
from datetime import datetime
from block import Block


class Blockchain:
   def __init__(self, difficulty: int = 2):
       self.chain: List[Block] = []
       self.pending_transactions: List[Dict[str, Any]] = []
       self.difficulty = difficulty
       self.mining_reward = 10.0
       self.create_genesis_block()
      


   def create_genesis_block(self) -> None:
       genesis_block = Block(
           index=0,
           transactions=[],
           timestamp=datetime.now().timestamp(),
           previous_hash="0" * 64
       )
       genesis_block.mine_block(self.difficulty)
       self.chain.append(genesis_block)

def get_latest_block(self) -> Block:
    return self.chain[-1]


def add_transaction(self, transaction: Dict[str, Any]) -> bool:
    if not transaction.get("sender") or not transaction.get("recipient"):
        return False
    if not transaction.get("amount") or transaction["amount"] <= 0:
        return False
    self.pending_transactions.append(transaction)
    return True
