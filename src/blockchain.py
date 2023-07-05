import json

from time import time
from Crypto.Hash import keccak


class Blockchain:
    """Defines a blockchain on an individual machine"""
    def __init__(self) -> None:
        self.chain = []
        self.transactions = []
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """ Create a new block """
        block = {"index": len(self.chain) + 1,
                 "time_stamp": time(),
                 "transactions": self.transactions,
                 "proof": proof,
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
    def hash(block):
        """Get hash of a block with Keccak hash function"""
        block_string = json.dumps(block, sort_keys=True).encode()
        k = keccak.new(digest_bits=256)
        k.update(block_string)
        return k.hexdigest()

    @property
    def last_block(self):
        """Get last block"""
        pass
