import json

from .base import BaseStorage


class CookieStorage(BaseStorage):
    encoder = json.JSONEncoder(separators=(',', ':'))

    def load_data(self):
        serialized_data = self.request.get_signed_cookie(
            self.prefix, default=None)
        if serialized_data is None:
            data = self.init_data()
        else:
            data = json.loads(data, cls=json.JSONDecoder)
        return data

    def update_response(self, response):
        super(CookieStorage, self).update_response(response)
        if self.data:
            response.set_signed_cookie(self.prefix,
                                       self.encoder.encode(self.data))
        else:
            response.delete_cookie(self.prefix)
