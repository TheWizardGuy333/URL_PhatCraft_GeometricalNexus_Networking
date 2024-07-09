class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(previous_hash='0')

    def create_block(self, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'transactions': self.transactions,
                 'previous_hash': previous_hash}
        self.transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
