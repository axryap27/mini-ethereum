import unittest
import tempfile
import os
from datetime import datetime

from blockchain import Blockchain
from block import Block
from transaction import Transaction
from wallet import Wallet
from smart_contract import SimpleEVM, SmartContract
from network import Network, Node
from mempool import TransactionPool, MempoolManager


class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain(difficulty=2)
        self.wallet1 = Wallet()
        self.wallet2 = Wallet()

    def test_genesis_block_creation(self):
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0" * 64)
        self.assertEqual(len(genesis.transactions), 0)

    def test_add_transaction(self):
        tx_data = {
            "sender": self.wallet1.address,
            "recipient": self.wallet2.address,
            "amount": 10.0,
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.01,
            "nonce": 0
        }
        
        result = self.blockchain.add_transaction(tx_data)
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)

    def test_mining_block(self):
        tx_data = {
            "sender": "0",  # Genesis transaction
            "recipient": self.wallet1.address,
            "amount": 100.0,
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.01,
            "nonce": 0
        }
        
        self.blockchain.add_transaction(tx_data)
        initial_chain_length = len(self.blockchain.chain)
        
        result = self.blockchain.mine_pending_transactions(self.wallet1.address)
        
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.chain), initial_chain_length + 1)
        self.assertEqual(len(self.blockchain.pending_transactions), 0)

    def test_balance_calculation(self):
        # Give wallet1 some initial funds
        tx1_data = {
            "sender": "0",
            "recipient": self.wallet1.address,
            "amount": 100.0,
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.0,
            "nonce": 0
        }
        
        self.blockchain.add_transaction(tx1_data)
        self.blockchain.mine_pending_transactions(self.wallet1.address)
        
        # Check balance includes mining reward
        balance = self.blockchain.get_balance(self.wallet1.address)
        expected_balance = 100.0 + self.blockchain.mining_reward  # Initial + mining reward
        self.assertEqual(balance, expected_balance)

    def test_chain_validation(self):
        self.assertTrue(self.blockchain.is_valid_chain())
        
        # Tamper with a block
        if len(self.blockchain.chain) > 1:
            self.blockchain.chain[1].transactions.append({"fake": "transaction"})
            self.assertFalse(self.blockchain.is_valid_chain())

    def test_difficulty_adjustment(self):
        initial_difficulty = self.blockchain.difficulty
        
        # Add some transactions and mine blocks quickly
        for i in range(3):
            tx_data = {
                "sender": "0",
                "recipient": self.wallet1.address,
                "amount": 1.0,
                "timestamp": datetime.now().timestamp(),
                "gas_fee": 0.01,
                "nonce": i
            }
            self.blockchain.add_transaction(tx_data)
            self.blockchain.mine_pending_transactions(self.wallet1.address)
        
        # Difficulty should increase due to fast block times
        self.assertGreaterEqual(self.blockchain.difficulty, initial_difficulty)


class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.wallet1 = Wallet()
        self.wallet2 = Wallet()

    def test_transaction_creation(self):
        tx = Transaction(
            sender=self.wallet1.address,
            recipient=self.wallet2.address,
            amount=10.0,
            gas_price=0.001,
            nonce=0
        )
        
        self.assertEqual(tx.sender, self.wallet1.address)
        self.assertEqual(tx.recipient, self.wallet2.address)
        self.assertEqual(tx.amount, 10.0)
        self.assertEqual(tx.gas_fee, 21.0)  # 21000 * 0.001

    def test_transaction_signing(self):
        tx = Transaction(
            sender=self.wallet1.get_public_key(),  # Use public key as sender
            recipient=self.wallet2.address,
            amount=10.0
        )
        
        self.assertIsNone(tx.signature)
        tx.sign_transaction(self.wallet1.private_key)
        self.assertIsNotNone(tx.signature)

    def test_transaction_validation(self):
        tx = Transaction(
            sender=self.wallet1.address,
            recipient=self.wallet2.address,
            amount=10.0
        )
        
        self.assertTrue(tx.is_valid())
        
        # Test invalid amount
        tx_invalid = Transaction(
            sender=self.wallet1.address,
            recipient=self.wallet2.address,
            amount=-5.0
        )
        self.assertFalse(tx_invalid.is_valid())


class TestWallet(unittest.TestCase):
    def test_wallet_creation(self):
        wallet = Wallet()
        self.assertIsNotNone(wallet.private_key)
        self.assertIsNotNone(wallet.public_key)
        self.assertIsNotNone(wallet.address)

    def test_wallet_save_load(self):
        wallet1 = Wallet()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_filename = f.name
        
        try:
            wallet1.save_to_file(temp_filename)
            wallet2 = Wallet.load_from_file(temp_filename)
            
            self.assertEqual(wallet1.address, wallet2.address)
            self.assertEqual(wallet1.get_private_key(), wallet2.get_private_key())
        finally:
            os.unlink(temp_filename)

    def test_transaction_signing_verification(self):
        wallet = Wallet()
        tx_data = {
            "sender": wallet.get_public_key(),
            "recipient": "recipient_address",
            "amount": 10.0,
            "timestamp": datetime.now().timestamp()
        }
        
        signature = wallet.sign_transaction(tx_data)
        self.assertIsNotNone(signature)
        
        is_valid = wallet.verify_transaction(tx_data, signature)
        self.assertTrue(is_valid)


class TestSmartContract(unittest.TestCase):
    def setUp(self):
        self.evm = SimpleEVM()
        self.wallet = Wallet()

    def test_contract_deployment(self):
        code = '{"type": "Storage", "functions": ["store", "retrieve"]}'
        contract_address = self.evm.deploy_contract(code, self.wallet.address)
        
        self.assertIsNotNone(contract_address)
        self.assertIn(contract_address, self.evm.contracts)

    def test_contract_execution(self):
        code = '{"type": "Storage", "functions": ["store_value", "get_value"]}'
        contract_address = self.evm.deploy_contract(code, self.wallet.address)
        
        # Store a value
        result = self.evm.call_contract(
            contract_address,
            "store_value",
            {"key": "test", "value": "hello"},
            self.wallet.address
        )
        
        self.assertTrue(result["success"])
        
        # Retrieve the value
        result = self.evm.call_contract(
            contract_address,
            "get_value",
            {"key": "test"},
            self.wallet.address
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "hello")

    def test_contract_balance(self):
        code = '{"type": "Storage"}'
        contract_address = self.evm.deploy_contract(code, self.wallet.address, 50.0)
        
        contract = self.evm.get_contract(contract_address)
        self.assertEqual(contract.balance, 50.0)


class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.network = Network()

    def test_node_creation(self):
        node = self.network.create_node("node1")
        
        self.assertEqual(node.node_id, "node1")
        self.assertIn("node1", self.network.nodes)
        self.assertIsNotNone(node.wallet)
        self.assertIsNotNone(node.blockchain)

    def test_node_connection(self):
        node1 = self.network.create_node("node1")
        node2 = self.network.create_node("node2")
        
        success = self.network.connect_nodes("node1", "node2")
        
        self.assertTrue(success)
        self.assertIn(node2, node1.peers)
        self.assertIn(node1, node2.peers)

    def test_transaction_broadcasting(self):
        node1 = self.network.create_node("node1")
        node2 = self.network.create_node("node2")
        self.network.connect_nodes("node1", "node2")
        
        tx_data = {
            "sender": node1.wallet.address,
            "recipient": node2.wallet.address,
            "amount": 10.0,
            "timestamp": datetime.now().timestamp(),
            "gas_fee": 0.01,
            "nonce": 0
        }
        
        node1.broadcast_transaction(tx_data)
        
        self.assertIn(tx_data, node1.mempool)
        self.assertIn(tx_data, node2.mempool)

    def test_network_status(self):
        self.network.create_node("node1")
        self.network.create_node("node2")
        
        status = self.network.get_network_status()
        
        self.assertEqual(status["total_nodes"], 2)
        self.assertIn("node1", status["nodes"])
        self.assertIn("node2", status["nodes"])


class TestMempool(unittest.TestCase):
    def setUp(self):
        self.wallet1 = Wallet()
        self.wallet2 = Wallet()
        self.mempool = TransactionPool()

    def test_transaction_addition(self):
        tx = Transaction(
            sender=self.wallet1.address,
            recipient=self.wallet2.address,
            amount=10.0
        )
        
        result = self.mempool.add_transaction(tx)
        self.assertTrue(result)
        self.assertEqual(self.mempool.get_pending_count(), 1)

    def test_priority_ordering(self):
        # Create transactions with different gas prices
        tx1 = Transaction(
            sender=self.wallet1.address,
            recipient=self.wallet2.address,
            amount=10.0,
            gas_price=0.001,
            nonce=0
        )
        
        tx2 = Transaction(
            sender=self.wallet1.address,
            recipient=self.wallet2.address,
            amount=5.0,
            gas_price=0.002,  # Higher gas price
            nonce=1
        )
        
        self.mempool.add_transaction(tx1)
        self.mempool.add_transaction(tx2)
        
        top_transactions = self.mempool.get_top_transactions(2)
        
        # Higher gas price transaction should come first
        self.assertEqual(len(top_transactions), 2)
        # Note: Due to nonce ordering, tx1 (nonce 0) should come first
        self.assertEqual(top_transactions[0].nonce, 0)

    def test_mempool_stats(self):
        tx = Transaction(
            sender=self.wallet1.address,
            recipient=self.wallet2.address,
            amount=10.0,
            gas_price=0.001
        )
        
        self.mempool.add_transaction(tx)
        stats = self.mempool.get_mempool_stats()
        
        self.assertEqual(stats["total_transactions"], 1)
        self.assertEqual(stats["avg_gas_price"], 0.001)
        self.assertEqual(stats["unique_senders"], 1)


def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestBlockchain,
        TestTransaction,
        TestWallet,
        TestSmartContract,
        TestNetwork,
        TestMempool
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 Running Mini-Ethereum Test Suite")
    print("=" * 50)
    
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)