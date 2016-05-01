from unittest import TestCase
from unittest.mock import MagicMock, patch, DEFAULT

from django.test.client import RequestFactory

from dynawizard.views import DynaWizard


class DynaWizardBaseTests(object):
    def setUp(self):
        self.request_factory = RequestFactory()

class DynaWizardGetTests(DynaWizardBaseTests, TestCase):
    def test_get(self):
        with patch.multiple(
            DynaWizard,
            get_form_instance=DEFAULT,
            render_step=DEFAULT,
        ) as mocks:
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
        ) as mocks:
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
            get_next_step=DEFAULT,
            redirect_to_step=DEFAULT,
        ) as mocks:
            wiz = DynaWizard()
            step = 'step'
            request = self.request_factory.post('')
            request.POST = {'key1': 'value1'}

            result = DynaWizard.as_view()(request, step=step)

            wiz.get_form_instance.assert_called_with(
                step=step,
                form_kwargs=request.POST,
            )

            wiz.get_next_step.assert_called_with(
                current_step=step,
            )

            self.assertEquals(result, wiz.redirect_to_step.return_value)
