from transaction import Transaction
from ecdsa import SigningKey, SECP256k1
import base58

def main():
    # Generate a new key pair for demonstration
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    
    # Convert public key to base58 for use as an address
    sender_address = base58.b58encode(public_key.to_string()).decode('utf-8')
    recipient_address = "recipient_address_here"  # In real usage, this would be another public key
    
    # Create a new transaction
    transaction = Transaction(
        sender=sender_address,
        recipient=recipient_address,
        amount=1.5  # Amount in ETH or your token
    )
    
    # Sign the transaction
    transaction.sign_transaction(private_key)
    
    # Verify the transaction
    is_valid = transaction.verify_signature()
    print(f"Transaction is valid: {is_valid}")
    
    # Print transaction details
    print("\nTransaction Details:")
    print(f"Sender: {transaction.sender}")
    print(f"Recipient: {transaction.recipient}")
    print(f"Amount: {transaction.amount}")
    print(f"Timestamp: {transaction.timestamp}")
    print(f"Hash: {transaction.hash}")
    print(f"Signature: {transaction.signature}")

if __name__ == "__main__":
    main() 