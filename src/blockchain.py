import json
import sys

from time import time
from Crypto.Hash import keccak
from flask import Flask, jsonify
from uuid import uuid4


class Blockchain:
    """Defines a blockchain on an individual machine"""
    def __init__(self) -> None:
        self.hardness = 4
        self.chain = []
        self.transactions = []
        self.new_block(proof_of_work=100, previous_hash=1)

    def new_block(self, proof_of_work, previous_hash=None):
        """ Create a new block """
        block = {"index": len(self.chain) + 1,
                 "time_stamp": time(),
                 "transactions": self.transactions,
                 "proof_of_work": proof_of_work,
                 "previous_hash": previous_hash or self.hash(self.chain[-1])
                }
        self.transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, receiver, amount):
        """Add a new tranaction to memopool"""
        self.transactions.append({"sender": sender, "receiver": receiver, "amount": amount})
        return self.last_block["index"] + 1
        
    @staticmethod
    def get_hash(string: str):
        """Returns the Keccak hash of a string"""
        tmp = keccak.new(digest_bits=256)
        tmp.update(string)
        return tmp.hexdigest()
    
    @staticmethod
    def get_block_hash(block):
        """Get hash of a block with Keccak hash function"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return Blockchain.get_hash(block_string)

    @property
    def last_block(self):
        """Get last block"""
        pass

    @staticmethod
    def proof_of_work_is_valid(self, previous_proof_of_work, proof_of_work):
        """Checks if given proof of work is valid"""
        to_be_checked = f"\"previous_proof_of_work\": {str(previous_proof_of_work)}, \"proof_of_work\": {str(proof_of_work)}"
        hash_of_to_be_checked = Blockchain.get_hash(to_be_checked)
        return hash_of_to_be_checked[:self.hardness] == "0" * self.hardness

    def proof_of_work(self, previous_proof_of_work):
        """Shows that work has been done by miner"""
        proof_of_work = 0
        while not Blockchain.proof_of_work_is_valid(previous_proof_of_work, proof_of_work):
            proof_of_work += 1
        
        return proof_of_work

app = Flask(__name__)
node_id = str(uuid4())
blockchain = Blockchain()

@app.route("/mine")
def mine():
    """This will mine a block and add it to the chain"""
    return "I will mine"

@app.route("/trxs/new", methods=["POST"])
def new_transactions():
    """Will add a new transactions"""
    return "A new transaction was added"

@app.route("/chain")
def full_chain():
    """Returns the full chain"""
    result = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=sys.argv[1])