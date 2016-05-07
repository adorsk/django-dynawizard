from unittest import TestCase
from unittest.mock import MagicMock, patch, DEFAULT

from django.test.client import RequestFactory

from dynawizard.views import DynaWizard
from dynawizard.storage.base import BaseStorage, LazyFormFiles, History


class BaseStorageTests(TestCase):
    def test_retrieve_form_files(self):
        with patch('dynawizard.storage.base.LazyFormFiles') as MockFormFiles:
            base_storage = BaseStorage()
            mock_stored_form_files = 'mock_stored_form_files'
            result = base_storage.retrieve_form_files(
                stored_form_files=mock_stored_form_files)
            MockFormFiles.assert_called_with(
                retrieve_form_file=base_storage.retrieve_form_file,
                stored_form_files=mock_stored_form_files)

    def test_retrieve_form_file(self):
        mock_opened_file = 'mock_opened_file'
        class MockFileStorage(object):
            def __init__(self):
                self.open = MagicMock(return_value=mock_opened_file)
        base_storage = BaseStorage(file_storage=MockFileStorage())
        stored_form_file = {'storage_key': 'storage_key'}
        result = base_storage.retrieve_form_file(stored_form_file)
        base_storage.file_storage.open.assert_called_with(
            stored_form_file['storage_key'])
        self.assertEquals(result, mock_opened_file)


class HistoryTests(TestCase):
    def test_get_item(self):
        mock_serialized_items = [0, 1, 2, 3]
        mock_deserialized_item = 'mock_deserialized_item'
        mock_deserialize_item = MagicMock(return_value=mock_deserialized_item)
        with patch.multiple(
            History,
            deserialize_item=mock_deserialize_item
        ):
            history = History(serialized_items=mock_serialized_items)
            item = history[0]
            self.assertEquals(item, mock_deserialized_item)

            items = history[0:-1]
            for item in items:
                self.assertEquals(item, mock_deserialized_item)

    def test_serialize_item(self):
        mock_stored_form_files = 'mock_stored_form_files'
        class MockStorage(object):
            def __init__(self):
                self.store_form_files = MagicMock(
                    return_value=mock_stored_form_files)
        mock_storage = MockStorage()
        history = History(storage=mock_storage)
        item = {
            'step': 'step',
            'form_data': {'k1': 'v1'},
            'form_files': 'mock_form_files',
        }
        serialized_item = history.serialize_item(item)
        mock_storage.store_form_files.assert_called_with(item['form_files'])
        self.assertEquals(serialized_item, {
            'step': item['step'],
            'form_data': item['form_data'],
            'stored_form_files': mock_stored_form_files,
        })

    def test_deserialize_item(self):
        mock_retrieved_form_files = 'mock_retrieved_form_files'
        class MockStorage(object):
            def __init__(self):
                self.retrieve_form_files = MagicMock(
                    return_value=mock_retrieved_form_files)
        mock_storage = MockStorage()
        history = History(storage=mock_storage)
        serialized_item = {
            'step': 'step',
            'form_data': {'k1': 'v1'},
            'stored_form_files': 'stored_form_files',
        }
        deserialized_item = history.deserialize_item(serialized_item)
        mock_storage.retrieve_form_files.assert_called_with(
            stored_form_files=serialized_item['stored_form_files'])
        self.assertEquals(deserialized_item, {
            'step': serialized_item['step'],
            'form_data': serialized_item['form_data'],
            'form_files': mock_retrieved_form_files,
        })

    def test_iter(self):
        with patch.multiple(
            History,
            __getitem__=MagicMock(return_value='mock_item')
        ):
            serialized_items = [1, 2, 3]
            history = History(serialized_items=serialized_items)
            counter = 0
            for item in history:
                counter += 1
            self.assertEquals(counter, len(serialized_items))


class LazyFormFilesTests(TestCase):
    def test_get_item(self):
        """Creates UploadedFile instance w/ result of
        retrieve_form_file."""
        mock_retrieved_file = {'id': 'mock_file'}
        mock_retrieve_form_file = MagicMock(return_value=mock_retrieved_file)
        mock_stored_files = {'file1': {
            'name': 'name',
            'charset': 'charset',
            'content_type': 'content_type',
            'size': 'size',
        }}
        with patch(
            'dynawizard.storage.base.UploadedFile',
            autospec=True
        ) as UploadedFile:
            lazy_form_files = LazyFormFiles(
                retrieve_form_file=mock_retrieve_form_file,
                stored_files=mock_stored_files,
            )
            lazy_form_files['file1']
            UploadedFile.assert_called_with(
                file=mock_retrieved_file,
                **mock_stored_files['file1']
            )



class DynaWizardBaseTests(object):
    def setUp(self):
        self.request_factory = RequestFactory()

    def get_storage_name_mock(self):
        return MagicMock(
            return_value='tests.dynawizardtests.test_storage.TestStorage')

class DynaWizardGetTests(DynaWizardBaseTests, TestCase):
    def test_get(self):
        with patch.multiple(
            DynaWizard,
            get_form_instance=DEFAULT,
            render_step=DEFAULT,
            get_storage_name=self.get_storage_name_mock()
        ):
            step = 'step'
            request = self.request_factory.get('')
            wiz = DynaWizard()
            result = DynaWizard.as_view()(request, step=step)
            wiz.get_form_instance.assert_called_with(
                step=step,
                form_kwargs={},
            )
            wiz.render_step.assert_called_with(
                request,
                step=step,
                context={
                    'form': wiz.get_form_instance.return_value
                }
            )
            self.assertEquals(result, wiz.render_step.return_value)

class DynaWizardPostTests(DynaWizardBaseTests, TestCase):

    def test_invalid_form(self):

        class InvalidForm():
            def is_valid(self):
                return False
        invalid_form = InvalidForm()

        with patch.multiple(
            DynaWizard,
            get_form_instance=MagicMock(return_value=invalid_form),
            render_step=DEFAULT,
            get_storage_name=self.get_storage_name_mock()
        ):
            wiz = DynaWizard()
            step = 'step'
            request = self.request_factory.post('')
            request.POST = {'key1': 'value1'}
            result = DynaWizard.as_view()(request, step=step)
            wiz.get_form_instance.assert_called_with(
                step=step,
                form_kwargs=request.POST,
            )
            wiz.render_step.assert_called_with(
                request,
                step=step,
                context={
                    'form': wiz.get_form_instance.return_value,
                }
            )
            self.assertEquals(result, wiz.render_step.return_value)


    def test_valid_form(self):

        class ValidForm():
            def is_valid(self):
                return True
        valid_form = ValidForm()

        with patch.multiple(
            DynaWizard,
            get_form_instance=MagicMock(return_value=valid_form),
            update_history=DEFAULT,
            after_process_step=DEFAULT,
            get_next_step=DEFAULT,
            redirect_to_step=DEFAULT,
            get_storage_name=self.get_storage_name_mock()
        ):
            wiz = DynaWizard()
            step = 'step'
            request = self.request_factory.post('')
            request.POST = {'key1': 'value1'}
            result = DynaWizard.as_view()(request, step=step)
            wiz.get_form_instance.assert_called_with(
                step=step,
                form_kwargs=request.POST,
            )
            wiz.update_history.assert_called_with(
                step=step,
                form=valid_form,
            )
            wiz.after_process_step.assert_called_with(
                step=step,
            )
            wiz.get_next_step.assert_called_with(
                current_step=step,
            )
            self.assertEquals(result, wiz.redirect_to_step.return_value)
