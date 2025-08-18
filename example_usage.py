#!/Users/aarya/opt/anaconda3/bin/python
"""
Mini-Ethereum Enhanced - Quick Example Usage

This script demonstrates the key features of the enhanced Mini-Ethereum blockchain:
- Enhanced blockchain with gas fees
- Smart contract deployment and interaction
- Multi-node network simulation
- Advanced transaction management
"""

from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from smart_contract import SimpleEVM, ContractBuilder
from network import Network
from datetime import datetime


def main():
    print("🚀 Mini-Ethereum Enhanced - Quick Example\n")
    
    # 1. Create Enhanced Blockchain
    print("1️⃣ Creating enhanced blockchain...")
    blockchain = Blockchain(difficulty=2)  # Lower difficulty for demo
    print(f"   ✅ Genesis block created: {blockchain.chain[0].hash[:16]}...")
    print(f"   ⚡ Network difficulty: {blockchain.difficulty}")
    
    # 2. Create Wallets
    print("\n2️⃣ Creating wallets...")
    alice = Wallet()
    bob = Wallet()
    print(f"   👤 Alice: {alice.address[:16]}...")
    print(f"   👤 Bob: {bob.address[:16]}...")
    
    # 3. Fund Alice's account (genesis transaction)
    print("\n3️⃣ Initial funding...")
    genesis_tx = {
        "sender": "0",
        "recipient": alice.address,
        "amount": 1000.0,
        "timestamp": datetime.now().timestamp(),
        "gas_fee": 0.0,
        "nonce": 0
    }
    blockchain.add_transaction(genesis_tx)
    print(f"   💰 Genesis: 1000 coins → Alice")
    
    # 4. Mine the first block
    print("\n4️⃣ Mining genesis block...")
    blockchain.mine_pending_transactions(alice.address)
    alice_balance = blockchain.get_balance(alice.address)
    print(f"   ⛏️  Block mined! Alice's balance: {alice_balance}")
    
    # 5. Create and send a transaction with gas
    print("\n5️⃣ Creating enhanced transaction...")
    tx = Transaction(
        sender=alice.address,
        recipient=bob.address,
        amount=100.0,
        gas_price=0.002,  # Higher gas price
        gas_limit=25000,
        nonce=blockchain.get_account_nonce(alice.address)
    )
    
    # Sign the transaction
    tx.sign_transaction(alice.private_key)
    blockchain.add_transaction(tx.to_dict())
    print(f"   💸 Transaction created: {tx.amount} coins")
    print(f"   ⛽ Gas fee: {tx.gas_fee}")
    print(f"   🔢 Nonce: {tx.nonce}")
    
    # 6. Mine the transaction
    print("\n6️⃣ Mining transaction block...")
    blockchain.mine_pending_transactions(bob.address)
    print(f"   💰 Alice's balance: {blockchain.get_balance(alice.address)}")
    print(f"   💰 Bob's balance: {blockchain.get_balance(bob.address)}")
    
    # 7. Smart Contract Demo
    print("\n7️⃣ Smart contract demonstration...")
    evm = SimpleEVM()
    
    # Deploy a storage contract
    storage_code = ContractBuilder.create_storage_contract()
    contract_address = evm.deploy_contract(storage_code, alice.address)
    print(f"   📋 Storage contract deployed: {contract_address[:16]}...")
    
    # Store some data
    result1 = evm.call_contract(
        contract_address,
        "store_value",
        {"key": "greeting", "value": "Hello, Blockchain!"},
        alice.address
    )
    print(f"   💾 Data stored: {result1['success']}")
    
    # Retrieve data
    result2 = evm.call_contract(
        contract_address,
        "get_value",
        {"key": "greeting"},
        bob.address
    )
    print(f"   📖 Retrieved: {result2['result']}")
    
    # 8. Network Simulation
    print("\n8️⃣ Network simulation...")
    network = Network()
    
    # Create nodes
    node1 = network.create_node("miner1")
    node2 = network.create_node("miner2")
    network.connect_nodes("miner1", "miner2")
    
    print(f"   🖥️  Created 2 connected nodes")
    print(f"   🔗 Node connections: {len(node1.peers)} peers each")
    
    # Simulate a network transaction
    success = network.simulate_transaction("miner1", "miner2", 25.0)
    if success:
        print(f"   💸 Network transaction broadcasted")
    
    # Get network status
    status = network.get_network_status()
    print(f"   📊 Network: {status['total_nodes']} nodes, {status['total_pending_transactions']} pending tx")
    
    # 9. Final Statistics
    print("\n9️⃣ Final blockchain statistics...")
    print(f"   📦 Total blocks: {len(blockchain.chain)}")
    print(f"   ⚡ Current difficulty: {blockchain.difficulty}")
    print(f"   🏦 Total accounts: {len(blockchain.accounts)}")
    print(f"   📊 Chain valid: {blockchain.is_valid_chain()}")
    
    print(f"\n✨ Demo completed successfully!")
    print(f"🎯 Try running: python demo.py for the interactive experience")
    print(f"🛠️  Or use: python enhanced_cli.py --help for CLI commands")


if __name__ == "__main__":
    main()