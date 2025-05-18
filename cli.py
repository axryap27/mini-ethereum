import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import argparse
from datetime import datetime
from blockchain import Blockchain
from wallet import Wallet
from miner import Miner
from utils import load_json_file, save_json_file, format_amount


class CLI:
   def __init__(self):
       self.blockchain = Blockchain.load_from_file('chain_data.json')
       self.wallet = None
       self.miner = None



   def create_wallet(self) -> None:
       self.wallet = Wallet()
       self.wallet.save_to_file('wallet.json')
       print(f"Wallet created with address: {self.wallet.address}")
       print("Wallet saved to wallet.json")


   def load_wallet(self) -> None:
       if os.path.exists('wallet.json'):
           self.wallet = Wallet.load_from_file('wallet.json')
           print(f"Wallet loaded with address: {self.wallet.address}")
       else:
           print("No wallet found. Create one with 'create_wallet' command.")


   def send_transaction(self, recipient: str, amount: float) -> None:
       if not self.wallet:
           print("No wallet loaded. Create or load a wallet first.")
           return


       transaction = {
           'sender': self.wallet.address,
           'recipient': recipient,
           'amount': amount,
           'timestamp': datetime.now().timestamp()
       }
       signature = self.wallet.sign_transaction(transaction)
       transaction['signature'] = signature


       if self.blockchain.add_transaction(transaction):
           print(f"Transaction created: {format_amount(amount)} to {recipient}")
       else:
           print("Failed to create transaction")


   def mine_block(self) -> None:
       if not self.wallet:
           print("No wallet loaded. Create or load a wallet first.")
           return


       if not self.blockchain.pending_transactions:
           print("No pending transactions to mine")
           return


       self.blockchain.mine_pending_transactions(self.wallet.address)
       print("Block mined successfully")


   def get_balance(self, address: str = None) -> None:
       if not address and not self.wallet:
           print("No wallet loaded and no address provided")
           return


       address = address or self.wallet.address
       balance = self.blockchain.get_balance(address)
       print(f"Balance for {address}: {format_amount(balance)}")


   def view_chain(self) -> None:
       for block in self.blockchain.chain:
           print(f"\nBlock #{block.index}")
           print(f"Hash: {block.hash}")
           print(f"Previous Hash: {block.previous_hash}")
           print(f"Transactions: {len(block.transactions)}")
           for tx in block.transactions:
               print(f"  {tx['sender']} -> {tx['recipient']}: {format_amount(tx['amount'])}")

   def save_chain(self) -> None:
       self.blockchain.save_to_file('chain_data.json')
       print("Blockchain saved to file")


def main():
    cli = CLI()
    parser = argparse.ArgumentParser(description='Mini-Ethereum CLI')
    subparsers = parser.add_subparsers(dest='command')


    # Create wallet
    subparsers.add_parser('create_wallet')


    # Send transaction
    tx_parser = subparsers.add_parser('send_tx')
    tx_parser.add_argument('--to', type=str, required=True)
    tx_parser.add_argument('--amount', type=float, required=True)


    # Mine block
    subparsers.add_parser('mine_block')


    # View chain
    subparsers.add_parser('view_chain')


    # Get balance
    balance_parser = subparsers.add_parser('get_balance')
    balance_parser.add_argument('--address', type=str)


    args = parser.parse_args()


    if args.command == 'create_wallet':
        cli.create_wallet()
    elif args.command == 'send_tx':
        cli.load_wallet()
        cli.send_transaction(args.to, args.amount)
    elif args.command == 'mine_block':
        cli.load_wallet()
        cli.mine_block()
    elif args.command == 'view_chain':
        cli.view_chain()
    elif args.command == 'get_balance':
        cli.get_balance(args.address)
    else:
        parser.print_help()


    cli.save_chain()


if __name__ == '__main__':
    main()
