import heapq
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from transaction import Transaction


class TransactionPool:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.transactions: Dict[str, Transaction] = {}
        self.priority_queue: List[Tuple[float, str]] = []
        self.nonce_map: Dict[str, List[Transaction]] = {}
        
    def add_transaction(self, transaction: Transaction) -> bool:
        if not transaction.is_valid():
            return False
            
        if transaction.hash in self.transactions:
            return False
            
        if len(self.transactions) >= self.max_size:
            self._remove_lowest_priority()
        
        self.transactions[transaction.hash] = transaction
        
        priority = self._calculate_priority(transaction)
        heapq.heappush(self.priority_queue, (-priority, transaction.hash))
        
        if transaction.sender not in self.nonce_map:
            self.nonce_map[transaction.sender] = []
        self.nonce_map[transaction.sender].append(transaction)
        self.nonce_map[transaction.sender].sort(key=lambda tx: tx.nonce)
        
        return True
    
    def remove_transaction(self, tx_hash: str) -> Optional[Transaction]:
        if tx_hash not in self.transactions:
            return None
            
        transaction = self.transactions.pop(tx_hash)
        
        if transaction.sender in self.nonce_map:
            self.nonce_map[transaction.sender] = [
                tx for tx in self.nonce_map[transaction.sender] 
                if tx.hash != tx_hash
            ]
            if not self.nonce_map[transaction.sender]:
                del self.nonce_map[transaction.sender]
        
        return transaction
    
    def get_top_transactions(self, count: int = 10) -> List[Transaction]:
        transactions = []
        temp_heap = []
        
        while self.priority_queue and len(transactions) < count:
            priority, tx_hash = heapq.heappop(self.priority_queue)
            
            if tx_hash in self.transactions:
                transaction = self.transactions[tx_hash]
                if self._can_execute_transaction(transaction):
                    transactions.append(transaction)
                else:
                    temp_heap.append((priority, tx_hash))
            
        for item in temp_heap:
            heapq.heappush(self.priority_queue, item)
        
        return transactions
    
    def _calculate_priority(self, transaction: Transaction) -> float:
        gas_price_weight = transaction.gas_price * 0.7
        time_weight = (time.time() - transaction.timestamp) * 0.3
        return gas_price_weight + time_weight
    
    def _can_execute_transaction(self, transaction: Transaction) -> bool:
        sender_transactions = self.nonce_map.get(transaction.sender, [])
        
        if not sender_transactions:
            return True
            
        expected_nonce = min(tx.nonce for tx in sender_transactions)
        return transaction.nonce == expected_nonce
    
    def _remove_lowest_priority(self) -> None:
        while self.priority_queue:
            priority, tx_hash = heapq.heappop(self.priority_queue)
            if tx_hash in self.transactions:
                self.remove_transaction(tx_hash)
                break
    
    def get_pending_count(self) -> int:
        return len(self.transactions)
    
    def get_transactions_by_sender(self, sender: str) -> List[Transaction]:
        return self.nonce_map.get(sender, [])
    
    def clear_old_transactions(self, max_age_seconds: int = 3600) -> int:
        current_time = time.time()
        to_remove = []
        
        for tx_hash, transaction in self.transactions.items():
            if current_time - transaction.timestamp > max_age_seconds:
                to_remove.append(tx_hash)
        
        for tx_hash in to_remove:
            self.remove_transaction(tx_hash)
        
        return len(to_remove)
    
    def get_mempool_stats(self) -> Dict[str, Any]:
        if not self.transactions:
            return {
                "total_transactions": 0,
                "avg_gas_price": 0,
                "min_gas_price": 0,
                "max_gas_price": 0,
                "unique_senders": 0
            }
        
        gas_prices = [tx.gas_price for tx in self.transactions.values()]
        
        return {
            "total_transactions": len(self.transactions),
            "avg_gas_price": sum(gas_prices) / len(gas_prices),
            "min_gas_price": min(gas_prices),
            "max_gas_price": max(gas_prices),
            "unique_senders": len(self.nonce_map)
        }


class MempoolManager:
    def __init__(self):
        self.pools: Dict[str, TransactionPool] = {}
        self.global_pool = TransactionPool(max_size=5000)
        
    def create_pool(self, pool_name: str, max_size: int = 1000) -> TransactionPool:
        pool = TransactionPool(max_size)
        self.pools[pool_name] = pool
        return pool
    
    def get_pool(self, pool_name: str) -> Optional[TransactionPool]:
        return self.pools.get(pool_name)
    
    def add_to_global_pool(self, transaction: Transaction) -> bool:
        return self.global_pool.add_transaction(transaction)
    
    def add_to_pool(self, pool_name: str, transaction: Transaction) -> bool:
        pool = self.get_pool(pool_name)
        if pool:
            return pool.add_transaction(transaction)
        return False
    
    def get_best_transactions_for_block(self, pool_name: str = None, 
                                      count: int = 100) -> List[Transaction]:
        if pool_name and pool_name in self.pools:
            return self.pools[pool_name].get_top_transactions(count)
        else:
            return self.global_pool.get_top_transactions(count)
    
    def cleanup_old_transactions(self, max_age_seconds: int = 3600) -> Dict[str, int]:
        results = {}
        
        results["global"] = self.global_pool.clear_old_transactions(max_age_seconds)
        
        for pool_name, pool in self.pools.items():
            results[pool_name] = pool.clear_old_transactions(max_age_seconds)
        
        return results
    
    def get_all_stats(self) -> Dict[str, Any]:
        stats = {
            "global_pool": self.global_pool.get_mempool_stats(),
            "named_pools": {}
        }
        
        for pool_name, pool in self.pools.items():
            stats["named_pools"][pool_name] = pool.get_mempool_stats()
        
        return stats