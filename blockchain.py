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

def mine_pending_transactions(self, miner_address: str) -> bool:
    if not self.pending_transactions:
        return False


    # Create reward transaction
    reward_tx = {
        "sender": "0",
        "recipient": miner_address,
        "amount": self.mining_reward,
        "timestamp": datetime.now().timestamp()
    }
    self.pending_transactions.append(reward_tx)


    # Create new block
    new_block = Block(
        index=len(self.chain),
        transactions=self.pending_transactions,
        timestamp=datetime.now().timestamp(),
        previous_hash=self.get_latest_block().hash
    )


    # Mine the block
    new_block.mine_block(self.difficulty)


    # Add to chain
    self.chain.append(new_block)
    self.pending_transactions = []
    return True


def is_valid_chain(self) -> bool:
    for i in range(1, len(self.chain)):
        current_block = self.chain[i]
        previous_block = self.chain[i-1]


        if current_block.hash != current_block.compute_hash():
            return False


        if current_block.previous_hash != previous_block.hash:
            return False

    return True


def get_balance(self, address: str) -> float:
    balance = 0.0
    for block in self.chain:
        for transaction in block.transactions:
            if transaction["recipient"] == address:
                balance += transaction["amount"]
            if transaction["sender"] == address:
                balance -= transaction["amount"]
    return balance


def save_to_file(self, filename: str) -> None:
    chain_data = [block.to_dict() for block in self.chain]
    with open(filename, 'w') as f:
        json.dump(chain_data, f, indent=4)


@classmethod
def load_from_file(cls, filename: str) -> 'Blockchain':
    blockchain = cls()
    try:
        with open(filename, 'r') as f:
            chain_data = json.load(f)
            blockchain.chain = [Block.from_dict(block_dict) for block_dict in chain_data]
    except FileNotFoundError:
        pass
    return blockchain
