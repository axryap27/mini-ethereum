# Mini-Ethereum

A simplified implementation of a blockchain system inspired by Ethereum. This project demonstrates the core concepts of blockchain technology including blocks, transactions, mining, and wallets.

## Features

- Block creation and validation
- Transaction processing with digital signatures
- Proof-of-Work mining
- Wallet creation and management
- Command-line interface for interaction
- Persistent blockchain storage

## Requirements

- Python 3.7+
- ecdsa
- base58

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install ecdsa base58
```

## Usage

The project provides a command-line interface for interacting with the blockchain. Here are the available commands:

### Create a wallet

```bash
python cli.py create_wallet
```

This will generate a new wallet and save it to `wallet.json`.

### Send a transaction

```bash
python cli.py send_tx --to <recipient_address> --amount <amount>
```

This will create and sign a transaction from your wallet to the recipient.

### Mine a block

```bash
python cli.py mine_block
```

This will mine pending transactions and add them to the blockchain.

### View the blockchain

```bash
python cli.py view_chain
```

This will display all blocks in the blockchain.

### Check balance

```bash
python cli.py get_balance [--address <address>]
```

This will show the balance for the specified address or your wallet if no address is provided.

## How Mining Works

1. Transactions are collected in a mempool
2. When mining starts:
   - A reward transaction is created for the miner
   - A new block is created with pending transactions
   - The block is mined using Proof-of-Work
   - The block is added to the chain
   - The mempool is cleared

## How Transactions Work

1. A transaction is created with sender, recipient, and amount
2. The transaction is signed using the sender's private key
3. The transaction is added to the mempool
4. Miners include the transaction in the next block
5. Once mined, the transaction is confirmed on the blockchain

## Project Structure

- `blockchain.py`: Main blockchain implementation
- `block.py`: Block structure and validation
- `transaction.py`: Transaction handling
- `wallet.py`: Wallet and key management
- `miner.py`: Mining operations
- `cli.py`: Command-line interface
- `utils.py`: Utility functions
- `chain_data.json`: Blockchain storage
- `wallet.json`: Wallet storage

## Security Notes

This is a simplified implementation for educational purposes. It should not be used for production purposes as it lacks many security features found in real blockchain implementations.

## License
