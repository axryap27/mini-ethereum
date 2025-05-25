import json
import hashlib
from typing import Dict, Any
from datetime import datetime
import base58
from ecdsa import SigningKey, VerifyingKey, SECP256k1

def hash_string(string: str) -> str:
    return hashlib.sha256(string.encode()).hexdigest()

def load_json_file(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json_file(filename: str, data: Dict[str, Any]) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def validate_address(address: str) -> bool:
    try:
        # Basic address validation
        if not address or len(address) < 26 or len(address) > 35:
            return False
        return True
    except:
        return False

def format_amount(amount: float) -> str:
    return f"{amount:.8f}"

def get_timestamp() -> float:
    return datetime.now().timestamp()

def serialize_key(key: SigningKey) -> str:
    return base58.b58encode(key.to_string()).decode('utf-8')

def deserialize_key(key_string: str) -> SigningKey:
    return SigningKey.from_string(
        base58.b58decode(key_string),
        curve=SECP256k1
    )

def format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') 