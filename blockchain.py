import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from block import Block


class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.difficulty = difficulty
        self.mining_reward = 10.0
        self.block_time = 15
        self.accounts: Dict[str, Dict[str, Any]] = {}
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
        
        sender_balance = self.get_balance(transaction["sender"])
        total_cost = transaction["amount"] + transaction.get("gas_fee", 0)
        
        if sender_balance < total_cost and transaction["sender"] != "0":
            return False
            
        self.pending_transactions.append(transaction)
        return True

    def mine_pending_transactions(self, miner_address: str) -> bool:
        if not self.pending_transactions:
            return False

        total_fees = sum(tx.get("gas_fee", 0) for tx in self.pending_transactions)
        
        reward_tx = {
            "sender": "0",
            "recipient": miner_address,
            "amount": self.mining_reward + total_fees,
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0
        }
        self.pending_transactions.append(reward_tx)

        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            timestamp=datetime.now().timestamp(),
            previous_hash=self.get_latest_block().hash
        )

        new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        self.update_account_states(new_block)
        self.pending_transactions = []
        self.adjust_difficulty()
        return True

    def update_account_states(self, block: Block) -> None:
        for transaction in block.transactions:
            sender = transaction["sender"]
            recipient = transaction["recipient"]
            amount = transaction["amount"]
            gas_fee = transaction.get("gas_fee", 0)
            
            if sender != "0":
                if sender not in self.accounts:
                    self.accounts[sender] = {"balance": 0, "nonce": 0}
                self.accounts[sender]["balance"] -= (amount + gas_fee)
                self.accounts[sender]["nonce"] += 1
            
            if recipient not in self.accounts:
                self.accounts[recipient] = {"balance": 0, "nonce": 0}
            self.accounts[recipient]["balance"] += amount

    def adjust_difficulty(self) -> None:
        if len(self.chain) < 2:
            return
        
        latest_block = self.get_latest_block()
        previous_block = self.chain[-2]
        time_taken = latest_block.timestamp - previous_block.timestamp
        
        if time_taken < self.block_time / 2:
            self.difficulty += 1
        elif time_taken > self.block_time * 2:
            self.difficulty = max(1, self.difficulty - 1)

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
        if address in self.accounts:
            return self.accounts[address]["balance"]
        
        balance = 0.0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction["recipient"] == address:
                    balance += transaction["amount"]
                if transaction["sender"] == address:
                    balance -= transaction["amount"] + transaction.get("gas_fee", 0)
        return balance

    def get_account_nonce(self, address: str) -> int:
        if address in self.accounts:
            return self.accounts[address]["nonce"]
        return 0

    def save_to_file(self, filename: str) -> None:
        chain_data = {
            "chain": [block.to_dict() for block in self.chain],
            "difficulty": self.difficulty,
            "accounts": self.accounts
        }
        with open(filename, 'w') as f:
            json.dump(chain_data, f, indent=4)

    @classmethod
    def load_from_file(cls, filename: str) -> 'Blockchain':
        blockchain = cls()
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    blockchain.chain = [Block.from_dict(block_dict) for block_dict in data]
                else:
                    blockchain.chain = [Block.from_dict(block_dict) for block_dict in data.get("chain", [])]
                    blockchain.difficulty = data.get("difficulty", 4)
                    blockchain.accounts = data.get("accounts", {})
        except FileNotFoundError:
            pass
        return blockchain
