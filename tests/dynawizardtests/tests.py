from unittest import TestCase
from unittest.mock import MagicMock, patch, DEFAULT

from django.test.client import RequestFactory

from dynawizard.views import DynaWizard


class DynaWizardTests(TestCase):
    def test_instantiation(self):
        dynawizard = DynaWizard()

    def test_get(self):
        with patch.multiple(
            DynaWizard,
            get_form_instance=DEFAULT,
            render_step=DEFAULT,
        ) as mocks:
            wiz = DynaWizard()
            step = 'step'
            result = wiz.get(None, step=step)

            self.assertEquals(result, mocks['render_step'].return_value)

            wiz.get_form_instance.assert_called_with(
                step=step,
                form_kwargs={},
            )

            wiz.render_step.assert_called_with(
                step=step,
                context={
                    'form': mocks['get_form_instance'].return_value
                }
            )
