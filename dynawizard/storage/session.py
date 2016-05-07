from .base import BaseStorage


class SessionStorage(BaseStorage):
    """Proxies 'data' attribute to session."""
    def _get_data(self):
        return self.request.session[self.prefix]

    def _set_data(self, value):
        self.request.session[self.prefix] = value
        self.request.session.modified = True
    data = property(_get_data, _set_data)

    def load_data(self):
        if self.prefix not in self.request.session:
            data = self.init_data()
        else:
            data = self.data
        return data
