import collections
from django.core.files.uploadedfile import UploadedFile
from django.utils import six


FILE_KWARG_NAMES = ['name', 'content_type', 'size', 'charset']


class BaseStorage(object):
    def __init__(self, prefix, request=None, file_storage=None):
        self.prefix = 'dynawizard_%s' % prefix
        self.request = request
        self.file_storage = file_storage
        self.data = self.load_data()
        self.history = self.load_history()

    def load_data(self):
        """Subclasses will implement this to load persisted data."""
        pass

    def init_data(self):
        return {
            'history': [],
            'session': {},
        }

    def load_history(self):
        return History(storage=self, serialized_items=self.data['history'])

    def store_form_files(self, form_files):
        stored_files = []
        for field, field_file in six.iteritems(form_files or {}):
            storage_key = self.file_storage.save(field_file.name, field_file)
            stored_file = {'storage_key': storage_key}.update(
                {file_kwarg: getattr(field_file, file_kwarg)
                 for file_kwarg in FILE_KWARG_NAMES}
            )
            stored_files.append(stored_file)
        return stored_files

    def retrieve_form_files(self, stored_form_files=None):
        return LazyFormFiles(
            retrieve_form_file=self.retrieve_form_file,
            stored_form_files=stored_form_files
        )

    def retrieve_form_file(self, stored_form_file=None):
        return self.file_storage.open(stored_form_file['storage_key'])

    def update_response(self, response):
        pass


class History(object):
    def __init__(self, storage=None, serialized_items=[]):
        self.serialized_items = serialized_items
        self.storage = storage

    @property
    def previous(self):
        return self[-1]

    def append_item(self, item=None):
        self.serialized_items.append(self.serialize_item(item))
        self.storage.data['history'] = self

    def serialize_item(self, item={}):
        serialized_item = {
            'step': item.get('step'),
            'form_data': item.get('form_data'),
            'stored_form_files': self.storage.store_form_files(
                item.get('form_files')),
        }
        return serialized_item

    def deserialize_item(self, serialized_item):
        return {
            'step': serialized_item['step'],
            'form_data': serialized_item['form_data'],
            'form_files': self.storage.proxy_stored_form_files(
                stored_form_files=serialized_item['stored_form_files'])
        }

    def __getitem__(self, key):
        serialized_item = self.serialized_items[key]
        if isinstance(serialized_item, collections.Iterable):
            history_item = [self.deserialize_item(slice_item)
                            for slice_item in serialized_item]
        else:
            history_item = self.deserialize_item(serialized_item)
        return history_item

    def __iter__(self):
        self._iter_idx = 0
        return self

    def __next__(self):
        if self._iter_idx > len(self.serialized_items):
            raise StopIteration
        else:
            item = self[self._iter_idx]
            self._iter_idx += 1
            return item


class LazyFormFiles(object):
    """A dict-like object that creates UploadedFile instances
    for stored files."""
    def __init__(self, retrieve_form_file=None, stored_files={}):
        self.retrieve_form_file = retrieve_form_file
        self.stored_files = stored_files
        self._uploaded_files = {}

    def __getattr__(self, name):
        if name == '__getitem__':
            return self.__getitem__
        elif name == '__setitem__' or name == '__delitem__':
            raise Exception("LazyFormFiles is read-only")
        else:
            return getattr(self.stored_files, name)

    def __getitem__(self, key):
        uploaded_file = self._uploaded_files.get(key)
        if not uploaded_file:
            stored_file = self.stored_files[key]
            file_kwargs = {file_kwarg: stored_file.get(file_kwarg)
                           for file_kwarg in FILE_KWARG_NAMES}
            uploaded_file = UploadedFile(
                file=self.retrieve_form_file(stored_file),
                **file_kwargs
            )
            self._uploaded_files[key] = uploaded_file
        return uploaded_file
