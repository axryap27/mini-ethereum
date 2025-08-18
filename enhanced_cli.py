import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from smart_contract import SimpleEVM, ContractBuilder
from network import Network, Node
from mempool import MempoolManager
from utils import load_json_file, save_json_file, format_amount


class EnhancedCLI:
    def __init__(self):
        self.blockchain = Blockchain.load_from_file('chain_data.json')
        self.wallet = None
        self.evm = SimpleEVM()
        self.network = Network()
        self.mempool_manager = MempoolManager()
        
    def create_wallet(self) -> None:
        self.wallet = Wallet()
        self.wallet.save_to_file('wallet.json')
        print(f"✅ Wallet created successfully!")
        print(f"Address: {self.wallet.address}")
        print(f"Public Key: {self.wallet.get_public_key()}")
        print("💾 Wallet saved to wallet.json")
        
    def load_wallet(self) -> None:
        if os.path.exists('wallet.json'):
            self.wallet = Wallet.load_from_file('wallet.json')
            print(f"✅ Wallet loaded: {self.wallet.address}")
        else:
            print("❌ No wallet found. Create one with 'create_wallet' command.")
            
    def send_transaction(self, recipient: str, amount: float, gas_price: float = 0.001) -> None:
        if not self.wallet:
            print("❌ No wallet loaded. Create or load a wallet first.")
            return
            
        nonce = self.blockchain.get_account_nonce(self.wallet.address)
        
        transaction = Transaction(
            sender=self.wallet.address,
            recipient=recipient,
            amount=amount,
            gas_price=gas_price,
            nonce=nonce
        )
        
        transaction.sign_transaction(self.wallet.private_key)
        
        if self.blockchain.add_transaction(transaction.to_dict()):
            print(f"✅ Transaction created successfully!")
            print(f"💰 Amount: {format_amount(amount)}")
            print(f"📧 To: {recipient}")
            print(f"⛽ Gas Fee: {format_amount(transaction.gas_fee)}")
            print(f"🔢 Nonce: {nonce}")
        else:
            print("❌ Failed to create transaction")
            
    def deploy_contract(self, contract_type: str, **kwargs) -> None:
        if not self.wallet:
            print("❌ No wallet loaded. Create or load a wallet first.")
            return
            
        if contract_type == "token":
            name = kwargs.get("name", "MyToken")
            symbol = kwargs.get("symbol", "MTK")
            supply = kwargs.get("supply", 1000)
            code = ContractBuilder.create_token_contract(name, symbol, supply)
        elif contract_type == "storage":
            code = ContractBuilder.create_storage_contract()
        elif contract_type == "voting":
            options = kwargs.get("options", ["Option A", "Option B"])
            code = ContractBuilder.create_voting_contract(options)
        else:
            print("❌ Unknown contract type. Available: token, storage, voting")
            return
            
        contract_address = self.evm.deploy_contract(code, self.wallet.address)
        print(f"✅ Contract deployed successfully!")
        print(f"📋 Contract Address: {contract_address}")
        print(f"📊 Contract Type: {contract_type}")
        
    def call_contract(self, contract_address: str, function: str, args: Dict[str, Any] = None) -> None:
        if not self.wallet:
            print("❌ No wallet loaded. Create or load a wallet first.")
            return
            
        args = args or {}
        result = self.evm.call_contract(contract_address, function, args, self.wallet.address)
        
        if result["success"]:
            print(f"✅ Contract call successful!")
            print(f"📊 Result: {result['result']}")
            print(f"⛽ Gas Used: {result['gas_used']}")
        else:
            print(f"❌ Contract call failed: {result['error']}")
            
    def mine_block(self) -> None:
        if not self.wallet:
            print("❌ No wallet loaded. Create or load a wallet first.")
            return
            
        if not self.blockchain.pending_transactions:
            print("❌ No pending transactions to mine")
            return
            
        print("⛏️  Mining block...")
        success = self.blockchain.mine_pending_transactions(self.wallet.address)
        
        if success:
            latest_block = self.blockchain.get_latest_block()
            print(f"✅ Block #{latest_block.index} mined successfully!")
            print(f"🔨 Block Hash: {latest_block.hash}")
            print(f"📦 Transactions: {len(latest_block.transactions)}")
            print(f"💰 Mining Reward: {format_amount(self.blockchain.mining_reward)}")
        else:
            print("❌ Mining failed")
            
    def get_balance(self, address: str = None) -> None:
        if not address and not self.wallet:
            print("❌ No wallet loaded and no address provided")
            return
            
        address = address or self.wallet.address
        balance = self.blockchain.get_balance(address)
        nonce = self.blockchain.get_account_nonce(address)
        
        print(f"💰 Balance for {address[:10]}...{address[-6:]}:")
        print(f"   Amount: {format_amount(balance)}")
        print(f"   Nonce: {nonce}")
        
    def view_chain(self) -> None:
        print(f"\n🔗 Blockchain Overview")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📊 Total Blocks: {len(self.blockchain.chain)}")
        print(f"⛏️  Difficulty: {self.blockchain.difficulty}")
        print(f"⏰ Block Time: {self.blockchain.block_time}s")
        
        for block in self.blockchain.chain[-5:]:  # Show last 5 blocks
            print(f"\n📦 Block #{block.index}")
            print(f"   Hash: {block.hash[:16]}...")
            print(f"   Previous: {block.previous_hash[:16]}...")
            print(f"   Transactions: {len(block.transactions)}")
            print(f"   Nonce: {block.nonce}")
            
            for i, tx in enumerate(block.transactions[:3]):  # Show first 3 transactions
                print(f"   💸 TX{i+1}: {tx['sender'][:8]}... → {tx['recipient'][:8]}... : {format_amount(tx['amount'])}")
                
    def create_network_node(self, node_id: str) -> None:
        node = self.network.create_node(node_id)
        print(f"✅ Network node '{node_id}' created")
        print(f"🌐 Port: {node.port}")
        print(f"📧 Address: {node.wallet.address}")
        
    def connect_nodes(self, node1_id: str, node2_id: str) -> None:
        success = self.network.connect_nodes(node1_id, node2_id)
        if success:
            print(f"✅ Connected {node1_id} ↔ {node2_id}")
        else:
            print(f"❌ Failed to connect nodes")
            
    def simulate_network(self, duration: int = 60) -> None:
        if len(self.network.nodes) < 2:
            print("❌ Need at least 2 nodes for network simulation")
            return
            
        print(f"🚀 Starting network simulation for {duration} seconds...")
        results = self.network.simulate_network_activity(duration)
        
        print(f"\n📊 Simulation Results:")
        print(f"   💸 Transactions: {results['transactions_sent']}")
        print(f"   📦 Blocks Mined: {results['blocks_mined']}")
        print(f"   👥 Nodes Participated: {results['nodes_participated']}")
        
    def network_status(self) -> None:
        status = self.network.get_network_status()
        
        print(f"\n🌐 Network Status")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"👥 Total Nodes: {status['total_nodes']}")
        print(f"📬 Pending Transactions: {status['total_pending_transactions']}")
        print(f"📊 Avg Chain Height: {status['average_chain_height']:.1f}")
        print(f"⚡ Network Difficulty: {status['network_difficulty']}")
        
        for node_id, node_status in status['nodes'].items():
            print(f"\n🖥️  Node: {node_id}")
            print(f"   📦 Blocks: {node_status['blockchain_height']}")
            print(f"   👥 Peers: {node_status['peers']}")
            print(f"   💰 Balance: {format_amount(node_status['balance'])}")
            print(f"   ⛏️  Mining: {'Yes' if node_status['is_mining'] else 'No'}")
            
    def mempool_stats(self) -> None:
        stats = self.mempool_manager.get_all_stats()
        
        print(f"\n📬 Mempool Statistics")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        global_stats = stats['global_pool']
        print(f"🌍 Global Pool:")
        print(f"   📊 Total Transactions: {global_stats['total_transactions']}")
        print(f"   ⛽ Avg Gas Price: {global_stats['avg_gas_price']:.6f}")
        print(f"   👥 Unique Senders: {global_stats['unique_senders']}")
        
    def save_chain(self) -> None:
        self.blockchain.save_to_file('chain_data.json')
        print("💾 Blockchain saved to chain_data.json")


def main():
    cli = EnhancedCLI()
    parser = argparse.ArgumentParser(description='Enhanced Mini-Ethereum CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Wallet commands
    subparsers.add_parser('create_wallet', help='Create a new wallet')
    subparsers.add_parser('load_wallet', help='Load existing wallet')

    # Transaction commands
    tx_parser = subparsers.add_parser('send_tx', help='Send a transaction')
    tx_parser.add_argument('--to', type=str, required=True, help='Recipient address')
    tx_parser.add_argument('--amount', type=float, required=True, help='Amount to send')
    tx_parser.add_argument('--gas_price', type=float, default=0.001, help='Gas price')

    # Mining commands
    subparsers.add_parser('mine_block', help='Mine a new block')

    # Blockchain commands
    subparsers.add_parser('view_chain', help='View the blockchain')
    
    balance_parser = subparsers.add_parser('get_balance', help='Check balance')
    balance_parser.add_argument('--address', type=str, help='Address to check')

    # Smart contract commands
    contract_parser = subparsers.add_parser('deploy_contract', help='Deploy a smart contract')
    contract_parser.add_argument('--type', type=str, required=True, 
                                choices=['token', 'storage', 'voting'], help='Contract type')
    contract_parser.add_argument('--name', type=str, help='Token name (for token contracts)')
    contract_parser.add_argument('--symbol', type=str, help='Token symbol (for token contracts)')
    contract_parser.add_argument('--supply', type=int, help='Token supply (for token contracts)')
    contract_parser.add_argument('--options', nargs='+', help='Voting options (for voting contracts)')

    call_parser = subparsers.add_parser('call_contract', help='Call a contract function')
    call_parser.add_argument('--address', type=str, required=True, help='Contract address')
    call_parser.add_argument('--function', type=str, required=True, help='Function name')
    call_parser.add_argument('--args', type=str, help='Arguments as JSON string')

    # Network commands
    node_parser = subparsers.add_parser('create_node', help='Create a network node')
    node_parser.add_argument('--id', type=str, required=True, help='Node ID')

    connect_parser = subparsers.add_parser('connect_nodes', help='Connect two nodes')
    connect_parser.add_argument('--node1', type=str, required=True, help='First node ID')
    connect_parser.add_argument('--node2', type=str, required=True, help='Second node ID')

    sim_parser = subparsers.add_parser('simulate_network', help='Simulate network activity')
    sim_parser.add_argument('--duration', type=int, default=60, help='Simulation duration in seconds')

    subparsers.add_parser('network_status', help='Show network status')
    subparsers.add_parser('mempool_stats', help='Show mempool statistics')

    args = parser.parse_args()

    if args.command == 'create_wallet':
        cli.create_wallet()
    elif args.command == 'load_wallet':
        cli.load_wallet()
    elif args.command == 'send_tx':
        cli.load_wallet()
        cli.send_transaction(args.to, args.amount, args.gas_price)
    elif args.command == 'mine_block':
        cli.load_wallet()
        cli.mine_block()
    elif args.command == 'view_chain':
        cli.view_chain()
    elif args.command == 'get_balance':
        if not args.address:
            cli.load_wallet()
        cli.get_balance(args.address)
    elif args.command == 'deploy_contract':
        cli.load_wallet()
        kwargs = {}
        if args.name:
            kwargs['name'] = args.name
        if args.symbol:
            kwargs['symbol'] = args.symbol
        if args.supply:
            kwargs['supply'] = args.supply
        if args.options:
            kwargs['options'] = args.options
        cli.deploy_contract(args.type, **kwargs)
    elif args.command == 'call_contract':
        cli.load_wallet()
        args_dict = json.loads(args.args) if args.args else {}
        cli.call_contract(args.address, args.function, args_dict)
    elif args.command == 'create_node':
        cli.create_network_node(args.id)
    elif args.command == 'connect_nodes':
        cli.connect_nodes(args.node1, args.node2)
    elif args.command == 'simulate_network':
        cli.simulate_network(args.duration)
    elif args.command == 'network_status':
        cli.network_status()
    elif args.command == 'mempool_stats':
        cli.mempool_stats()
    else:
        parser.print_help()

    cli.save_chain()


if __name__ == '__main__':
    main()