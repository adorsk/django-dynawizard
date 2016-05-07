from dynawizard.storage.base import BaseStorage

class TestStorage(BaseStorage):
    def load_data(self):
        return self.init_data()
