from unittest import TestCase
from unittest.mock import MagicMock, patch, DEFAULT

from django.test.client import RequestFactory

from dynawizard.views import DynaWizard


class DynaWizardTests(TestCase):
    def test_instantiation(self):
        dynawizard = DynaWizard()

    def test_get(self):
        mock_specs = {
            'get_altered_form_kwargs': {'arg1': 'value1'},
            'get_form_instance': 'form_instance',
            'render_step': 'rendered_step',
        }
        mocks = {}
        for key, value in mock_specs.items():
            mocks[key] = MagicMock(return_value=value)

        with patch.multiple(DynaWizard, **mocks):
            wiz = DynaWizard()
            step = 'step'

            result = wiz.get(None, step=step)
            self.assertEquals(result, mocks['render_step'].return_value)

            wiz.get_altered_form_kwargs.assert_called_with(
                step=step,
                form_kwargs={},
            )
            wiz.get_form_instance.assert_called_with(
                step=step,
                form_kwargs=mocks['get_altered_form_kwargs'].return_value,
            )
            wiz.render_step.assert_called_with(
                step=step,
                context={
                    'form': mocks['get_form_instance'].return_value
                }
            )
