import json
import sys
import requests

from time import time
from Crypto.Hash import keccak
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:
    """Defines a blockchain on an individual machine"""
    def __init__(self) -> None:
        self.amount = 50
        self.hardness = 4
        self.nodes = set()
        self.chain = []
        self.transactions = []
        self.new_block(previous_hash=1)
        self.set_block_proof_of_work(self.last_block)

    def add_node(self, address):
        """Adds a new node to nodes"""
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def chain_is_valid(self, chain):
        """Check if chain is valid"""
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block["previous_hash"] != self.get_block_hash(chain[current_index-1]):
                return False
            if not self.proof_of_work_is_valid(block=block):
                return False
            current_index += 1
            return True
        
    def resolve_conflicts(self):
        """Selects longest valid chain"""
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbors:
            response = requests.get(f"http://{node}/chain")
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                if length > max_length and self.chain_is_valid(chain=chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        else:
            return False

    def new_block(self, previous_hash="None"):
        """ Create a new block """
        block = {"index": len(self.chain) + 1,
                 "time_stamp": time(),
                 "transactions": self.transactions,
                 "proof_of_work": 0,
                 "previous_hash": previous_hash or self.hash(self.chain[-1])
                }
        self.transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, receiver, amount):
        """Add a new tranaction to memopool"""
        self.transactions.append({"sender": sender, "receiver": receiver, "amount": amount})
        return self.last_block
        
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
        return self.chain[-1]

    def proof_of_work_is_valid(self, block):
        """Checks if given proof of work is valid"""
        hash_of_to_be_checked = Blockchain.get_block_hash(block)
        return hash_of_to_be_checked[:self.hardness] == "0" * self.hardness

    def set_block_proof_of_work(self, block):
        """Shows that work has been done by miner"""
        while not self.proof_of_work_is_valid(block):
            block["proof_of_work"] += 1
        
        return block

app = Flask(__name__)
node_id = str(uuid4())
blockchain = Blockchain()

@app.route("/mine", methods=["GET"])
def mine():
    """This will mine a block and add it to the chain"""
    if len(blockchain.transactions) == 0:
        response = {"message": "mempool is empty"}
        return jsonify(response), 400
    
    blockchain.new_transaction(sender="0", receiver=f"{node_id}", amount=blockchain.amount)
    new_block = blockchain.new_block(Blockchain.get_block_hash(blockchain.last_block))
    new_block = blockchain.set_block_proof_of_work(blockchain.last_block)
    response = {"message": "new block mined",
            "index": new_block["index"],
            "transactions": new_block["transactions"],
            "proof_of_work": new_block["proof_of_work"],
            "previous_hash": new_block["previous_hash"]}
    
    return jsonify(response), 200
    

@app.route("/trxs/new", methods=["POST"])
def new_transaction():
    """Will add a new transaction by getting sender and receiver and amount"""
    values = request.get_json()
    new_block = blockchain.new_transaction(values["sender"], values["receiver"], values["amount"])
    response = {"message": f"{new_block} will be added to transactions"}
    return jsonify(response), 201

@app.route("/trxs/all", methods=["GET"])
def get_transactions():
    """Will return current transactions in blockchain that have not been processed"""
    result = {
        'chain': blockchain.transactions,
        'length': len(blockchain.transactions)
    }
    return jsonify(result), 200

@app.route("/chain", methods=["GET"])
def full_chain():
    """Returns the full chain"""
    result = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(result), 200

@app.route("/nodes/register", methods=["POST"])
def register_node():
    """Registers new node"""
    values = request.get_json()
    nodes = values.get("nodes")

    for node in nodes:
        blockchain.add_node(node)
    
    response = {"message": "nodes added",
                "total_nodes": list(blockchain.nodes)}
    
    return jsonify(response), 201

@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    """Reaches consensus with other nodes based on their current chain"""
    replaced = blockchain.resolve_conflicts()
    response = {}
    if replaced:
        response = {
            "message": "replaced chain with longer chain",
            "new_chain": blockchain.chain
        }
    else:
        response = {
            "message": "my chain is longest valid chain",
            "new_chain": blockchain.chain
        }

    return jsonify(response), 200

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=sys.argv[1]) 
    finally:
        with open(f"{node_id}.text", "wb") as f:
            f.write(json.dumps(blockchain.chain).encode())
