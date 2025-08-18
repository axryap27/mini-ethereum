import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime


class SmartContract:
    def __init__(self, contract_address: str, code: str, creator: str, 
                 initial_balance: float = 0):
        self.contract_address = contract_address
        self.code = code
        self.creator = creator
        self.balance = initial_balance
        self.storage: Dict[str, Any] = {}
        self.created_at = datetime.now().timestamp()
        
    def execute(self, function_name: str, args: Dict[str, Any], 
                caller: str, value: float = 0) -> Dict[str, Any]:
        gas_used = 21000
        
        try:
            if function_name == "transfer" and "to" in args and "amount" in args:
                return self._transfer(args["to"], args["amount"], caller)
            elif function_name == "get_balance":
                return {"success": True, "result": self.balance, "gas_used": gas_used}
            elif function_name == "store_value" and "key" in args and "value" in args:
                return self._store_value(args["key"], args["value"], caller)
            elif function_name == "get_value" and "key" in args:
                return self._get_value(args["key"])
            else:
                return {"success": False, "error": "Function not found", "gas_used": gas_used}
        except Exception as e:
            return {"success": False, "error": str(e), "gas_used": gas_used}
    
    def _transfer(self, to: str, amount: float, caller: str) -> Dict[str, Any]:
        gas_used = 30000
        
        if self.balance < amount:
            return {"success": False, "error": "Insufficient balance", "gas_used": gas_used}
        
        self.balance -= amount
        return {
            "success": True, 
            "result": f"Transferred {amount} to {to}", 
            "gas_used": gas_used,
            "transfers": [{"to": to, "amount": amount}]
        }
    
    def _store_value(self, key: str, value: Any, caller: str) -> Dict[str, Any]:
        gas_used = 20000
        self.storage[key] = value
        return {"success": True, "result": f"Stored {key}={value}", "gas_used": gas_used}
    
    def _get_value(self, key: str) -> Dict[str, Any]:
        gas_used = 5000
        value = self.storage.get(key, None)
        return {"success": True, "result": value, "gas_used": gas_used}
    
    def receive_ether(self, amount: float) -> None:
        self.balance += amount
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_address": self.contract_address,
            "code": self.code,
            "creator": self.creator,
            "balance": self.balance,
            "storage": self.storage,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, contract_dict: Dict[str, Any]) -> 'SmartContract':
        contract = cls(
            contract_address=contract_dict["contract_address"],
            code=contract_dict["code"],
            creator=contract_dict["creator"],
            initial_balance=contract_dict["balance"]
        )
        contract.storage = contract_dict.get("storage", {})
        contract.created_at = contract_dict.get("created_at", datetime.now().timestamp())
        return contract


class SimpleEVM:
    def __init__(self):
        self.contracts: Dict[str, SmartContract] = {}
        self.next_contract_id = 1
    
    def deploy_contract(self, code: str, creator: str, initial_value: float = 0) -> str:
        contract_address = self._generate_contract_address(creator, self.next_contract_id)
        self.next_contract_id += 1
        
        contract = SmartContract(contract_address, code, creator, initial_value)
        self.contracts[contract_address] = contract
        
        return contract_address
    
    def call_contract(self, contract_address: str, function_name: str, 
                     args: Dict[str, Any], caller: str, value: float = 0) -> Dict[str, Any]:
        if contract_address not in self.contracts:
            return {"success": False, "error": "Contract not found", "gas_used": 21000}
        
        contract = self.contracts[contract_address]
        
        if value > 0:
            contract.receive_ether(value)
        
        return contract.execute(function_name, args, caller, value)
    
    def get_contract(self, contract_address: str) -> Optional[SmartContract]:
        return self.contracts.get(contract_address)
    
    def _generate_contract_address(self, creator: str, nonce: int) -> str:
        data = f"{creator}{nonce}".encode()
        return "0x" + hashlib.sha256(data).hexdigest()[:40]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contracts": {addr: contract.to_dict() for addr, contract in self.contracts.items()},
            "next_contract_id": self.next_contract_id
        }
    
    @classmethod
    def from_dict(cls, evm_dict: Dict[str, Any]) -> 'SimpleEVM':
        evm = cls()
        evm.next_contract_id = evm_dict.get("next_contract_id", 1)
        
        for addr, contract_data in evm_dict.get("contracts", {}).items():
            evm.contracts[addr] = SmartContract.from_dict(contract_data)
        
        return evm


class ContractBuilder:
    @staticmethod
    def create_token_contract(name: str, symbol: str, total_supply: int) -> str:
        return json.dumps({
            "type": "ERC20",
            "name": name,
            "symbol": symbol,
            "total_supply": total_supply,
            "functions": ["transfer", "balance_of", "approve", "allowance"]
        })
    
    @staticmethod
    def create_storage_contract() -> str:
        return json.dumps({
            "type": "Storage",
            "functions": ["store_value", "get_value"]
        })
    
    @staticmethod
    def create_voting_contract(options: List[str]) -> str:
        return json.dumps({
            "type": "Voting",
            "options": options,
            "functions": ["vote", "get_results", "get_winner"]
        })