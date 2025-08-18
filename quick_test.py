#!/usr/bin/env python3
"""
Quick test to verify all components are working
"""

def test_imports():
    print("🧪 Testing imports...")
    try:
        import ecdsa
        import base58
        print("✅ Dependencies: ecdsa, base58")
        
        from blockchain import Blockchain
        from wallet import Wallet
        from transaction import Transaction
        print("✅ Core modules: blockchain, wallet, transaction")
        
        from smart_contract import SimpleEVM
        from network import Network
        from mempool import TransactionPool
        print("✅ Enhanced modules: smart_contract, network, mempool")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    print("\n🧪 Testing basic functionality...")
    try:
        from blockchain import Blockchain
        from wallet import Wallet
        
        # Create blockchain
        blockchain = Blockchain(difficulty=1)
        print(f"✅ Blockchain created with {len(blockchain.chain)} block")
        
        # Create wallets
        alice = Wallet()
        bob = Wallet()
        print(f"✅ Wallets created")
        print(f"   Alice: {alice.address[:16]}...")
        print(f"   Bob: {bob.address[:16]}...")
        
        # Test transaction
        from datetime import datetime
        tx_data = {
            "sender": "0",
            "recipient": alice.address,
            "amount": 100.0,
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.0,
            "nonce": 0
        }
        
        blockchain.add_transaction(tx_data)
        blockchain.mine_pending_transactions(alice.address)
        
        balance = blockchain.get_balance(alice.address)
        print(f"✅ Transaction processed, Alice balance: {balance}")
        
        return True
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Mini-Ethereum Quick Test\n")
    
    success1 = test_imports()
    success2 = test_basic_functionality()
    
    if success1 and success2:
        print("\n✅ All tests passed! The blockchain is working correctly.")
        print("🎯 You can now run:")
        print("   python example_usage.py")
        print("   python enhanced_cli.py --help")
        print("   python demo.py")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")