#!/Users/aarya/opt/anaconda3/bin/python

import time
import json
from datetime import datetime

from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from smart_contract import SimpleEVM, ContractBuilder
from network import Network
from mempool import MempoolManager


def print_header(title):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")


def print_step(step_num, description):
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 40)


def demo_basic_blockchain():
    print_header("BASIC BLOCKCHAIN DEMONSTRATION")
    
    print_step(1, "Creating a new blockchain")
    blockchain = Blockchain(difficulty=3)
    print(f"✅ Blockchain created with {len(blockchain.chain)} block(s)")
    print(f"⚡ Difficulty: {blockchain.difficulty}")
    print(f"💰 Mining reward: {blockchain.mining_reward}")
    
    print_step(2, "Creating wallets")
    alice = Wallet()
    bob = Wallet()
    charlie = Wallet()
    
    print(f"👤 Alice: {alice.address[:20]}...")
    print(f"👤 Bob: {bob.address[:20]}...")
    print(f"👤 Charlie: {charlie.address[:20]}...")
    
    print_step(3, "Adding initial transactions")
    # Genesis transactions to give Alice some coins
    genesis_tx = {
        "sender": "0",
        "recipient": alice.address,
        "amount": 1000.0,
        "timestamp": datetime.now().timestamp(),
        "gas_fee": 0.0,
        "nonce": 0
    }
    
    blockchain.add_transaction(genesis_tx)
    print(f"💸 Genesis transaction: 1000 coins to Alice")
    
    print_step(4, "Mining the first block")
    success = blockchain.mine_pending_transactions(alice.address)
    if success:
        latest_block = blockchain.get_latest_block()
        print(f"⛏️  Block #{latest_block.index} mined successfully!")
        print(f"🔨 Hash: {latest_block.hash[:32]}...")
        print(f"📦 Transactions: {len(latest_block.transactions)}")
        print(f"💰 Alice's balance: {blockchain.get_balance(alice.address)}")
    
    print_step(5, "Creating and mining more transactions")
    # Alice sends money to Bob and Charlie
    tx1_data = {
        "sender": alice.address,
        "recipient": bob.address,
        "amount": 100.0,
        "timestamp": datetime.now().timestamp(),
        "gas_fee": 1.0,
        "nonce": blockchain.get_account_nonce(alice.address)
    }
    
    tx2_data = {
        "sender": alice.address,
        "recipient": charlie.address,
        "amount": 50.0,
        "timestamp": datetime.now().timestamp(),
        "gas_fee": 1.0,
        "nonce": blockchain.get_account_nonce(alice.address) + 1
    }
    
    blockchain.add_transaction(tx1_data)
    blockchain.add_transaction(tx2_data)
    
    print(f"💸 Alice → Bob: 100 coins")
    print(f"💸 Alice → Charlie: 50 coins")
    
    # Mine the block
    blockchain.mine_pending_transactions(bob.address)  # Bob mines this block
    
    print_step(6, "Final balances")
    print(f"💰 Alice: {blockchain.get_balance(alice.address)}")
    print(f"💰 Bob: {blockchain.get_balance(bob.address)}")
    print(f"💰 Charlie: {blockchain.get_balance(charlie.address)}")
    
    print(f"\n📊 Blockchain Stats:")
    print(f"   📦 Total blocks: {len(blockchain.chain)}")
    print(f"   ⚡ Current difficulty: {blockchain.difficulty}")
    print(f"   📬 Pending transactions: {len(blockchain.pending_transactions)}")
    
    return blockchain, alice, bob, charlie


def demo_smart_contracts(blockchain, alice, bob):
    print_header("SMART CONTRACTS DEMONSTRATION")
    
    print_step(1, "Setting up EVM")
    evm = SimpleEVM()
    print("✅ EVM initialized")
    
    print_step(2, "Deploying a storage contract")
    storage_code = ContractBuilder.create_storage_contract()
    storage_address = evm.deploy_contract(storage_code, alice.address)
    print(f"📋 Storage contract deployed at: {storage_address[:20]}...")
    
    print_step(3, "Interacting with storage contract")
    # Store some data
    result1 = evm.call_contract(
        storage_address,
        "store_value",
        {"key": "user_count", "value": 42},
        alice.address
    )
    
    result2 = evm.call_contract(
        storage_address,
        "store_value",
        {"key": "app_name", "value": "Mini-Ethereum"},
        alice.address
    )
    
    print(f"💾 Stored user_count: {result1['success']}")
    print(f"💾 Stored app_name: {result2['success']}")
    
    # Retrieve data
    result3 = evm.call_contract(
        storage_address,
        "get_value",
        {"key": "user_count"},
        bob.address
    )
    
    result4 = evm.call_contract(
        storage_address,
        "get_value",
        {"key": "app_name"},
        bob.address
    )
    
    print(f"📖 Retrieved user_count: {result3['result']}")
    print(f"📖 Retrieved app_name: {result4['result']}")
    
    print_step(4, "Deploying a token contract")
    token_code = ContractBuilder.create_token_contract("DemoToken", "DEMO", 10000)
    token_address = evm.deploy_contract(token_code, alice.address)
    print(f"🪙 Token contract deployed at: {token_address[:20]}...")
    
    print_step(5, "Token contract interactions")
    balance_result = evm.call_contract(
        token_address,
        "get_balance",
        {},
        alice.address
    )
    
    print(f"💰 Token contract balance: {balance_result['result']}")
    
    return evm


def demo_network_simulation():
    print_header("NETWORK SIMULATION DEMONSTRATION")
    
    print_step(1, "Creating network nodes")
    network = Network()
    
    # Create 5 nodes
    nodes = []
    for i in range(5):
        node_id = f"node_{i+1}"
        node = network.create_node(node_id)
        nodes.append(node)
        print(f"🖥️  Created {node_id} on port {node.port}")
    
    print_step(2, "Connecting nodes in a mesh network")
    network.create_full_mesh()
    
    # Verify connections
    for node in nodes:
        print(f"🔗 {node.node_id} connected to {len(node.peers)} peers")
    
    print_step(3, "Simulating initial funding")
    # Give each node some initial funds
    for i, node in enumerate(nodes):
        tx_data = {
            "sender": "0",  # Genesis
            "recipient": node.wallet.address,
            "amount": 100.0 * (i + 1),  # Different amounts
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.0,
            "nonce": 0
        }
        node.blockchain.add_transaction(tx_data)
    
    # Mine initial blocks
    for node in nodes[:3]:  # Let first 3 nodes mine
        node.start_mining()
        time.sleep(0.1)
    
    print_step(4, "Simulating network transactions")
    transaction_count = 0
    
    # Create some inter-node transactions
    for i in range(10):
        sender_node = nodes[i % len(nodes)]
        recipient_node = nodes[(i + 1) % len(nodes)]
        
        tx_data = {
            "sender": sender_node.wallet.address,
            "recipient": recipient_node.wallet.address,
            "amount": 5.0 + (i * 0.5),
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.1,
            "nonce": sender_node.blockchain.get_account_nonce(sender_node.wallet.address)
        }
        
        sender_node.broadcast_transaction(tx_data)
        transaction_count += 1
        print(f"💸 TX{i+1}: {sender_node.node_id} → {recipient_node.node_id}: {tx_data['amount']}")
        time.sleep(0.05)
    
    print(f"📊 Total transactions broadcasted: {transaction_count}")
    
    print_step(5, "Mining transactions")
    blocks_mined = 0
    for node in nodes[:3]:  # Let nodes compete to mine
        if node.mempool:
            block = node.start_mining()
            if block:
                blocks_mined += 1
                print(f"⛏️  {node.node_id} mined block #{block.index}")
                break
    
    print_step(6, "Network status")
    status = network.get_network_status()
    print(f"🌐 Network overview:")
    print(f"   👥 Total nodes: {status['total_nodes']}")
    print(f"   📬 Pending transactions: {status['total_pending_transactions']}")
    print(f"   📊 Average chain height: {status['average_chain_height']:.1f}")
    
    for node_id, node_status in status['nodes'].items():
        print(f"   🖥️  {node_id}: {node_status['blockchain_height']} blocks, "
              f"{node_status['balance']:.2f} balance")
    
    return network


def demo_mempool_management():
    print_header("MEMPOOL MANAGEMENT DEMONSTRATION")
    
    print_step(1, "Setting up mempool manager")
    mempool_manager = MempoolManager()
    
    # Create wallets for demonstration
    wallets = [Wallet() for _ in range(3)]
    print(f"👥 Created {len(wallets)} test wallets")
    
    print_step(2, "Creating transactions with different gas prices")
    transactions = []
    
    for i in range(10):
        tx = Transaction(
            sender=wallets[i % 3].address,
            recipient=wallets[(i + 1) % 3].address,
            amount=10.0 + i,
            gas_price=0.001 + (i * 0.0005),  # Increasing gas prices
            nonce=i // 3  # Multiple transactions per sender
        )
        
        transactions.append(tx)
        mempool_manager.add_to_global_pool(tx)
        print(f"📝 TX{i+1}: {tx.amount} coins, gas price: {tx.gas_price}")
    
    print_step(3, "Mempool statistics")
    stats = mempool_manager.get_all_stats()
    global_stats = stats['global_pool']
    
    print(f"📊 Mempool stats:")
    print(f"   📦 Total transactions: {global_stats['total_transactions']}")
    print(f"   ⛽ Average gas price: {global_stats['avg_gas_price']:.6f}")
    print(f"   📈 Max gas price: {global_stats['max_gas_price']:.6f}")
    print(f"   📉 Min gas price: {global_stats['min_gas_price']:.6f}")
    print(f"   👥 Unique senders: {global_stats['unique_senders']}")
    
    print_step(4, "Getting top priority transactions")
    top_transactions = mempool_manager.get_best_transactions_for_block(count=5)
    
    print(f"⭐ Top 5 priority transactions:")
    for i, tx in enumerate(top_transactions, 1):
        print(f"   {i}. Amount: {tx.amount}, Gas Price: {tx.gas_price}, "
              f"Sender: {tx.sender[:10]}...")


def main():
    print("""
🌟 Welcome to Mini-Ethereum Enhanced Demo!
    
This demonstration will showcase:
✨ Basic blockchain functionality
🏗️  Smart contract deployment and execution  
🌐 Multi-node network simulation
📬 Advanced mempool management
    """)
    
    input("Press Enter to start the demonstration...")
    
    try:
        # Run all demonstrations
        blockchain, alice, bob, charlie = demo_basic_blockchain()
        
        input("\nPress Enter to continue to smart contracts demo...")
        evm = demo_smart_contracts(blockchain, alice, bob)
        
        input("\nPress Enter to continue to network simulation...")
        network = demo_network_simulation()
        
        input("\nPress Enter to continue to mempool demo...")
        demo_mempool_management()
        
        print_header("DEMONSTRATION COMPLETE")
        print("""
🎉 Congratulations! You've seen all the major features:

✅ Enhanced blockchain with gas fees and difficulty adjustment
✅ Smart contracts with storage and token functionality  
✅ Multi-node network simulation with P2P communication
✅ Advanced mempool with priority queue management
✅ Comprehensive account state tracking
✅ Professional CLI interface

🚀 Your Mini-Ethereum blockchain is now ready for development!
        """)
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred during the demo: {e}")
        print("Please check the logs for more details.")


if __name__ == "__main__":
    main()