import collections
from django.core.files.uploadedfile import UploadedFile
from django.utils.datastructures import MultiValueDict
from django.utils.functional import lazy_property
from django.utils import six

from .exceptions import NoFileStorageConfigured

class History(object):
    def __init__(self, storage=None, serialized_items=[]):
        self.serialized_items = serialized_items
        self.parent_storage = storage

    @property
    def previous(self):
        return self[-1]

    def append(self, value):
        self.serialized_items.append(value)
        self.parent_storage.data['history'] = self

    def __getitem__(self, key):
        serialized_item = self.serialized_items[key]
        if isinstance(serialized_item, collections.Iterable):
            history_item = [self.deserialize_item(slice_item)
                            for slice_item in serialized_item]
        else:
            history_item = self.deserialize_item(serialized_item)
        return history_item

    def deserialize_item(self, serialized_item):
        return HistoryItem(file_storage=self.parent_storage.file_storage,
                           **serialized_item)

class HistoryItem(object):
    def __init__(self, step=None, form_data=None, form_files=None,
                 file_storage=None):
        self.step = step
        self.form_data = form_data
        self.form_files = [
            LazyUploadedFile(form_file, file_storage=file_storage)
            for form_file in form_files]

class LazyUploadedFile():
    def __init__(self, file_storage=None):
        self.file_storage = file_storage

class BaseStorage(object):
    def __init__(self, prefix, request=None, file_storage=None):
        self.prefix = 'dynawizard_%s' % prefix
        self.request = request
        self.file_storage = file_storage

    def init_data(self):
        self.data = {
            'history': [],
            'session': {},
        }

    def update_history(self, step=None, form_data=None, form_files=None):
        history_item = {
            'step': step,
            'form_data': form_data,
            'form_files': self.store_form_files(form_files)
        }
        self.history.append(history_item)

    def store_form_files(self, form_files):
        stored_files = []
        for field, field_file in six.iteritems(form_files or {}):
            storage_key = self.file_storage.save(field_file.name, field_file)
            stored_file = {
                'storage_key': storage_key,
                'name': field_file.name,
                'content_type': field_file.content_type,
                'size': field_file.size,
                'charset': field_file.charset
            }
            stored_files.append(stored_file)
        return stored_files

    def _get_history(self):
        return History(storage=self, items=self.data['history'])
    history = lazy_property(_get_history)

    def update_response(self, response):
        pass
