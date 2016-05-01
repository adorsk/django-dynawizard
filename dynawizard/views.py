from django.shortcuts import render


class DynaWizard(object):
    def get(self, request, step=None):
        form_kwargs = {}
        altered_form_kwargs = self.get_altered_form_kwargs(
            step=step, form_kwargs=form_kwargs)
        form = self.get_form_instance(step=step, form_kwargs=altered_form_kwargs)
        return self.render_step(step=step, context={
            'form': form,
        })

    def get_altered_form_kwargs(self, step=None, form_kwargs={}):
        return form_kwargs

    def get_form_instance(self, step=None, form_kwargs={}):
        form_class = self.get_form_class(step=step)
        form_instance = form_class(**form_kwargs)
        return form_instance

    def get_form_class(self, step=None):
        form_class = None
        return form_class

    def render_step(self, step=None, context={}):
        altered_context = self.alter_render_context(step=step, context=context)
        template_name = self.get_template_name(step=step)
        return render(self.request, template_name, context=altered_context)

    def get_template_name(self, step=None):
        pass

    def post(self, step=None):
        # Get form class for step.
        # Generate form kwargs.
        # Alter form kwargs.
        # Instantiate form.
        # If form is invalid:
            # render step
        # Update history.
        # Get next step.
        # if not next_step:
            # self.done()
        # else:
            # Redirect to next_step.
        pass
