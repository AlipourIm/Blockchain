class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.transactions = []

    def new_block(self):
        """ Create a new block """
        pass

    def new_transactions(self):
        """Add a new tranaction to memopool"""
        pass

    @staticmethod
    def hash(block):
        """Get hash of a block"""
        pass

    def last_block(self):
        """Get last block"""
        pass
