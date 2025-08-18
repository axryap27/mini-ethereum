#!/Users/aarya/opt/anaconda3/bin/python
"""
Mini-Ethereum Getting Started Script

This script sets up your blockchain with initial funds so you can start experimenting.
"""

import os
from blockchain import Blockchain
from wallet import Wallet
from datetime import datetime


def setup_blockchain():
    print("🚀 Setting up your Mini-Ethereum blockchain...")
    
    # Create or load blockchain
    blockchain = Blockchain.load_from_file('chain_data.json')
    print(f"✅ Blockchain loaded with {len(blockchain.chain)} blocks")
    
    # Create or load wallet
    if os.path.exists('wallet.json'):
        wallet = Wallet.load_from_file('wallet.json')
        print(f"✅ Wallet loaded: {wallet.address[:20]}...")
    else:
        wallet = Wallet()
        wallet.save_to_file('wallet.json')
        print(f"✅ New wallet created: {wallet.address[:20]}...")
    
    # Check current balance
    current_balance = blockchain.get_balance(wallet.address)
    print(f"💰 Current balance: {current_balance}")
    
    # Give initial funds if needed
    if current_balance < 10:
        print("💸 Adding initial funds...")
        
        # Genesis transaction
        genesis_tx = {
            'sender': '0',
            'recipient': wallet.address,
            'amount': 1000.0,
            'timestamp': datetime.now().timestamp(),
            'gas_fee': 0.0,
            'nonce': 0
        }
        
        blockchain.add_transaction(genesis_tx)
        blockchain.mine_pending_transactions(wallet.address)
        
        new_balance = blockchain.get_balance(wallet.address)
        print(f"✅ Funds added! New balance: {new_balance}")
    else:
        print("✅ You already have sufficient funds")
    
    # Save everything
    blockchain.save_to_file('chain_data.json')
    print("💾 Blockchain saved")
    
    print(f"""
🎉 Setup complete! You can now:

📝 Basic Commands:
   python enhanced_cli.py get_balance
   python enhanced_cli.py view_chain
   python enhanced_cli.py send_tx --to ADDRESS --amount 50
   python enhanced_cli.py mine_block

🏗️ Smart Contracts:
   python enhanced_cli.py deploy_contract --type storage
   python enhanced_cli.py deploy_contract --type token --name "MyCoin" --symbol "MC"

🌐 Network Simulation:
   python enhanced_cli.py create_node --id alice
   python enhanced_cli.py network_status

📚 Full Tutorial:
   cat TUTORIAL.md

🎮 Interactive Demo:
   python demo.py

💰 Your address: {wallet.address}
💰 Your balance: {blockchain.get_balance(wallet.address)}
""")


if __name__ == "__main__":
    setup_blockchain()