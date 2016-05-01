from django.shortcuts import render, redirect
from django.views.generic.base import View

from .storage import get_storage


class DynaWizard(View):

    http_method_names = ['get', 'post', 'options']

    def dispatch(self, request, *args, **kwargs):
        self.prefix = self.get_prefix(request, *args, **kwargs)
        self.storage = get_storage(
            storage_name=self.storage_name,
            prefix=self.get_prefix(request, *args, **kwargs)
            request=request,
            file_storage=getattr(self, 'file_storage', None),
        )
        self.history = self.storage.history
        self.session = self.storage.session
        response = super(DynaWizard, self).dispatch(request, *args, **kwargs)
        self.storage.update_response(response)
        return response

    def get_prefix(self, request, *args, **kwargs):
        # TODO: Add some kind of unique id to prefix
        return self.__class__.__name__

    def get(self, request, step=None, **kwargs):
        form = self.get_form_instance(step=step, form_kwargs={})
        return self.render_step(request, step=step, context={
            'form': form,
        })

    def get_form_instance(self, step=None, form_kwargs={}):
        form_class = self.get_form_class(step=step)
        altered_form_kwargs = self.get_altered_form_kwargs(
            step=step, form_kwargs=form_kwargs)
        form_instance = form_class(**altered_form_kwargs)
        return form_instance

    def get_form_class(self, step=None):
        form_class = None
        return form_class

    def get_altered_form_kwargs(self, step=None, form_kwargs={}):
        return form_kwargs

    def render_step(self, request, step=None, context={}):
        altered_context = self.alter_render_context(step=step, context=context)
        template_name = self.get_template_name(step=step)
        return render(request, template_name, context=altered_context)

    def get_template_name(self, step=None):
        pass

    def post(self, request, step=None, **kwargs):
        form = self.get_form_instance(step=step, form_kwargs=request.POST)
        if not form.is_valid():
            return self.render_step(request, step=step, context={
                'form': form,
            })
        else:
            self.update_history(step=step, form=form)
            self.after_process_step(step=step)
            next_step = self.get_next_step(current_step=step)
            return self.redirect_to_step(step=next_step)

    def update_history(self, step=None, form=None):
        history_item = {
            'step': step,
            'form_data': getattr(form, 'cleaned_data', None),
            'form_files': getattr(form, 'files', None),
        }
        self.history.append(history_item)

    def after_process_step(self, step=None):
        pass

    def get_next_step(self, current_step=None):
        pass

    def redirect_to_step(self, step=None):
        redirect(self.base_url, step=step)
