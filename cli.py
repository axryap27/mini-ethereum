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