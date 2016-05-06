from .base import BaseStorage


class SessionStorage(BaseStorage):
    def ensure_data_is_initialized(self):
        if self.prefix not in self.request.session:
            self.init_data()

    def _get_data(self):
        return self.request.session[self.prefix]
    def _set_data(self, value):
        self.request.session[self.prefix] = value
        self.request.session.modified = True
    data = property(_get_data, _set_data)
