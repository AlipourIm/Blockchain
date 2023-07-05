class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.transactions = []

    def new_block(self):
        """ Create a new block """
        pass

    def new_transaction(self, sender, receiver, amount):
        """Add a new tranaction to memopool"""
        self.transactions.append({"sender": sender, "receiver": receiver, "amount": amount})

    @staticmethod
    def hash(block):
        """Get hash of a block"""
        pass

    def last_block(self):
        """Get last block"""
        pass
