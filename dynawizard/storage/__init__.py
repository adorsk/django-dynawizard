from django.utils.module_loading import import_string

from .base import BaseStorage
from .exceptions import MissingStorage, NoFileStorageConfigured

__all__ = [
    "BaseStorage", "MissingStorage", "NoFileStorageConfigured", "get_storage",
]


def get_storage(path, *args, **kwargs):
    try:
        storage_class = import_string(path)
    except ImportError as e:
        raise MissingStorage('Error loading storage: %s' % e)
    return storage_class(*args, **kwargs)

class HistoryItem(object):
    def __init__(self, step=None, form_data=None, form_files=None):
        self.step = step
        self.form_data = form_data
        self.form_files = form_files

def serialize_history_item(history_item):
    return {
        'step': history_item.step,
        'form_data': history_item.form_data,
        'form_files': [serialize_form_file(form_file)
                       for form_file in getattr(
                           history_item, 'form_files', [])]
    }

def deserialize_history_item(serialized_history_item):
    return HistoryItem(
        'step': serialized_history_item['step'],
        'form_data': history_item.form_data,
        'form_files': [deserialize_form_file(serialized_form_file)
                       for serialized_form_file in getattr(
                           serialized_history_item, 'form_files', [])]
    )

def serialize_form_file(form_file):
    return {
        'name': form_file.file_name,
        'temporary_file_path': form_file.temporary_file_path(),
        'content_type': form_file.content_type,
        'size': form_file.size,
        'charset': form_file.charset,
        'content_type_extra': form_file.content_type_extra,
    }

def deserialize_form_file(serialized_form_file):
    return UploadedFile(**serialized_form_file)
