import json
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from blockchain import Blockchain
from wallet import Wallet
from smart_contract import SimpleEVM


class Node:
    def __init__(self, node_id: str, port: int = 8000):
        self.node_id = node_id
        self.port = port
        self.blockchain = Blockchain()
        self.evm = SimpleEVM()
        self.peers: List['Node'] = []
        self.is_mining = False
        self.wallet = Wallet()
        self.mempool: List[Dict[str, Any]] = []
        
    def add_peer(self, peer: 'Node') -> None:
        if peer not in self.peers and peer.node_id != self.node_id:
            self.peers.append(peer)
            peer.peers.append(self)
    
    def broadcast_transaction(self, transaction: Dict[str, Any]) -> None:
        self.mempool.append(transaction)
        for peer in self.peers:
            if transaction not in peer.mempool:
                peer.receive_transaction(transaction)
    
    def receive_transaction(self, transaction: Dict[str, Any]) -> None:
        if transaction not in self.mempool:
            self.mempool.append(transaction)
            self.blockchain.add_transaction(transaction)
    
    def broadcast_block(self, block) -> None:
        for peer in self.peers:
            peer.receive_block(block)
    
    def receive_block(self, block) -> bool:
        if len(self.blockchain.chain) < len([block]) or block.index > len(self.blockchain.chain):
            return False
        
        if self.blockchain.chain[-1].hash == block.previous_hash:
            self.blockchain.chain.append(block)
            self.mempool.clear()
            return True
        return False
    
    def start_mining(self) -> Optional[Any]:
        if not self.mempool:
            return None
        
        self.is_mining = True
        
        for transaction in self.mempool[:10]:
            self.blockchain.add_transaction(transaction)
        
        success = self.blockchain.mine_pending_transactions(self.wallet.address)
        
        if success:
            new_block = self.blockchain.get_latest_block()
            self.broadcast_block(new_block)
            self.mempool.clear()
            self.is_mining = False
            return new_block
        
        self.is_mining = False
        return None
    
    def sync_with_peer(self, peer: 'Node') -> None:
        if len(peer.blockchain.chain) > len(self.blockchain.chain):
            if peer.blockchain.is_valid_chain():
                self.blockchain = peer.blockchain
                self.evm = peer.evm
    
    def deploy_contract(self, code: str, initial_value: float = 0) -> str:
        return self.evm.deploy_contract(code, self.wallet.address, initial_value)
    
    def call_contract(self, contract_address: str, function_name: str, 
                     args: Dict[str, Any], value: float = 0) -> Dict[str, Any]:
        return self.evm.call_contract(contract_address, function_name, args, 
                                    self.wallet.address, value)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "port": self.port,
            "blockchain_height": len(self.blockchain.chain),
            "peers": len(self.peers),
            "mempool_size": len(self.mempool),
            "is_mining": self.is_mining,
            "balance": self.blockchain.get_balance(self.wallet.address),
            "contracts": len(self.evm.contracts)
        }


class Network:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.network_difficulty = 4
        
    def create_node(self, node_id: str, port: int = None) -> Node:
        if port is None:
            port = 8000 + len(self.nodes)
        
        node = Node(node_id, port)
        node.blockchain.difficulty = self.network_difficulty
        self.nodes[node_id] = node
        return node
    
    def connect_nodes(self, node1_id: str, node2_id: str) -> bool:
        if node1_id in self.nodes and node2_id in self.nodes:
            node1 = self.nodes[node1_id]
            node2 = self.nodes[node2_id]
            node1.add_peer(node2)
            return True
        return False
    
    def create_full_mesh(self) -> None:
        node_list = list(self.nodes.values())
        for i, node1 in enumerate(node_list):
            for node2 in node_list[i+1:]:
                node1.add_peer(node2)
    
    def simulate_transaction(self, sender_id: str, recipient_id: str, amount: float) -> bool:
        if sender_id not in self.nodes or recipient_id not in self.nodes:
            return False
        
        sender_node = self.nodes[sender_id]
        recipient_node = self.nodes[recipient_id]
        
        transaction = {
            "sender": sender_node.wallet.address,
            "recipient": recipient_node.wallet.address,
            "amount": amount,
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.01,
            "nonce": sender_node.blockchain.get_account_nonce(sender_node.wallet.address)
        }
        
        sender_node.broadcast_transaction(transaction)
        return True
    
    def simulate_mining_round(self) -> Dict[str, Any]:
        results = {}
        miners = random.sample(list(self.nodes.values()), min(3, len(self.nodes)))
        
        for miner in miners:
            if miner.mempool:
                block = miner.start_mining()
                if block:
                    results[miner.node_id] = {
                        "success": True,
                        "block_index": block.index,
                        "transactions": len(block.transactions)
                    }
                    break
                else:
                    results[miner.node_id] = {"success": False}
        
        return results
    
    def get_network_status(self) -> Dict[str, Any]:
        total_transactions = sum(len(node.mempool) for node in self.nodes.values())
        avg_chain_height = sum(len(node.blockchain.chain) for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0
        
        return {
            "total_nodes": len(self.nodes),
            "total_pending_transactions": total_transactions,
            "average_chain_height": avg_chain_height,
            "network_difficulty": self.network_difficulty,
            "nodes": {node_id: node.get_status() for node_id, node in self.nodes.items()}
        }
    
    def save_network_state(self, filename: str) -> None:
        network_data = {
            "network_difficulty": self.network_difficulty,
            "nodes": {}
        }
        
        for node_id, node in self.nodes.items():
            network_data["nodes"][node_id] = {
                "node_id": node.node_id,
                "port": node.port,
                "blockchain": [block.to_dict() for block in node.blockchain.chain],
                "wallet_address": node.wallet.address,
                "evm": node.evm.to_dict()
            }
        
        with open(filename, 'w') as f:
            json.dump(network_data, f, indent=4)
    
    def simulate_network_activity(self, duration_seconds: int = 60) -> Dict[str, Any]:
        print(f"Simulating network activity for {duration_seconds} seconds...")
        
        start_time = time.time()
        results = {
            "transactions_sent": 0,
            "blocks_mined": 0,
            "nodes_participated": set()
        }
        
        while time.time() - start_time < duration_seconds:
            if len(self.nodes) >= 2 and random.random() < 0.3:
                sender_id, recipient_id = random.sample(list(self.nodes.keys()), 2)
                amount = round(random.uniform(0.1, 10.0), 2)
                
                if self.simulate_transaction(sender_id, recipient_id, amount):
                    results["transactions_sent"] += 1
                    results["nodes_participated"].add(sender_id)
                    results["nodes_participated"].add(recipient_id)
            
            if random.random() < 0.2:
                mining_results = self.simulate_mining_round()
                for node_id, result in mining_results.items():
                    if result.get("success"):
                        results["blocks_mined"] += 1
                        results["nodes_participated"].add(node_id)
            
            time.sleep(1)
        
        results["nodes_participated"] = len(results["nodes_participated"])
        return results