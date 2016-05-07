from django.utils.module_loading import import_string

from .base import BaseStorage
from .exceptions import MissingStorage, NoFileStorageConfigured

__all__ = [
    "BaseStorage", "MissingStorage", "NoFileStorageConfigured", "get_storage",
]


def get_storage(storage_name, *args, **kwargs):
    try:
        storage_class = import_string(storage_name)
    except ImportError as e:
        raise MissingStorage('Error loading storage: %s' % e)
    return storage_class(*args, **kwargs)
