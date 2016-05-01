from unittest import TestCase
from unittest.mock import MagicMock, patch, DEFAULT

from django.test.client import RequestFactory

from dynawizard.views import DynaWizard


class DynaWizardTests(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()

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

    #def test_post(self):
        #with patch.multiple(
            #DynaWizard,
            #get_form_instance=DEFAULT,
        #) as mocks:
            #wiz = DynaWizard()
            #step = 'step'
            #result = wiz.post(None, step=step)

            #self.assertEquals(result, mocks['render_step'].return_value)

            #wiz.get_form_instance.assert_called_with(
                #step=step,
                #form_kwargs={},
            #)

            #wiz.render_step.assert_called_with(
                #step=step,
                #context={
                    #'form': mocks['get_form_instance'].return_value
                #}
            #)
