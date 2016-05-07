from unittest import TestCase
from unittest.mock import MagicMock, patch, DEFAULT

from django.test.client import RequestFactory

from dynawizard.views import DynaWizard
from dynawizard.storage.base import LazyFormFiles, History


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

class HistoryTests(DynaWizardBaseTests, TestCase):
    def test_(self):
        pass

