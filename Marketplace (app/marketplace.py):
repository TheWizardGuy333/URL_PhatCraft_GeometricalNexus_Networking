class Marketplace:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.items = []

    def add_item(self, item_data):
        item = {'id': len(self.items) + 1, 'data': item_data}
        self.items.append(item)
        self.blockchain.add_transaction('system', item['data']['creator'], item['data']['price'])
        return item

    def get_items(self):
        return self.items
