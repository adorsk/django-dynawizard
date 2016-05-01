from django.core.files.uploadedfile import UploadedFile
from django.utils.datastructures import MultiValueDict
from django.utils.functional import lazy_property
from django.utils import six

from .exceptions import NoFileStorageConfigured

class History(list):
    def __init__(self, storage=None, items=[]):
        super(History, self).__init__(items)
        self.storage = storage

    @property
    def previous(self):
        return self[-1]

    def append(self, value):
        super(History, self).append(value)
        self.storage.data['history'] = self

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

    def _get_history(self):
        return History(storage=self, items=self.data['history'])
    history = lazy_property(_get_history)

    def get_files(self, step):
        wizard_files = self.data[self.step_files_key].get(step, {})

        if wizard_files and not self.file_storage:
            raise NoFileStorageConfigured(
                "You need to define 'file_storage' in your "
                "wizard view in order to handle file uploads.")

        files = {}
        for field, field_dict in six.iteritems(wizard_files):
            field_dict = field_dict.copy()
            tmp_name = field_dict.pop('tmp_name')
            if (step, field) not in self._files:
                self._files[(step, field)] = UploadedFile(
                    file=self.file_storage.open(tmp_name), **field_dict)
            files[field] = self._files[(step, field)]
        return files or None

    def set_files(self, step, files):
        if files and not self.file_storage:
            raise NoFileStorageConfigured(
                "You need to define 'file_storage' in your "
                "wizard view in order to handle file uploads.")

        if step not in self.data[self.step_files_key]:
            self.data[self.step_files_key][step] = {}

        for field, field_file in six.iteritems(files or {}):
            tmp_filename = self.file_storage.save(field_file.name, field_file)
            file_dict = {
                'tmp_name': tmp_filename,
                'name': field_file.name,
                'content_type': field_file.content_type,
                'size': field_file.size,
                'charset': field_file.charset
            }
            self.data[self.step_files_key][step][field] = file_dict

    def update_response(self, response):
        def post_render_callback(response):
            for file in self._get_files():
                if not file.closed:
                    file.close()
            for tmp_file in self._get_tmp_files():
                self.file_storage.delete(tmp_file)

        if hasattr(response, 'render'):
            response.add_post_render_callback(post_render_callback)
        else:
            post_render_callback(response)
