import time
from typing import Optional
from blockchain import Blockchain
from wallet import Wallet


class Miner:
   def __init__(self, blockchain: Blockchain, wallet: Wallet):
       self.blockchain = blockchain
       self.wallet = wallet
       self.is_mining = False


