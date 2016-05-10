from django.shortcuts import render, redirect
from django.views.generic.base import View

from . import storage


class DynaWizard(View):

    http_method_names = ['get', 'post', 'options']

    def dispatch(self, request, *args, **kwargs):
        self.prefix = self.get_prefix(request, *args, **kwargs)
        self.storage = self.get_storage(request, *args, **kwargs)
        response = super(DynaWizard, self).dispatch(request, *args, **kwargs)
        self.storage.update_response(response)
        return response

    def get_storage(self, request, *args, **kwargs):
        return storage.get_storage(
            storage_name=self.get_storage_name(),
            prefix=self.get_prefix(request, *args, **kwargs),
            request=request,
            file_storage=getattr(self, 'file_storage', None),
        )

    def get_prefix(self, request, *args, **kwargs):
        return self.__class__.__name__

    def get_storage_name(self):
        return 'dynawizard.storage.session.SessionStorage'

    def get(self, request, step=None, **kwargs):
        form = self.get_form_instance(step=step, form_kwargs={})
        return self.render_step(request, step=step, context={
            'form': form,
        })

    def get_form_instance(self, step=None, form_kwargs={}):
        form_instance = None
        form_class = self.get_form_class(step=step)
        if form_class:
            altered_form_kwargs = self.get_altered_form_kwargs(
                step=step, form_kwargs=form_kwargs)
            form_instance = form_class(altered_form_kwargs)
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
        if form and not form.is_valid():
            return self.render_step(request, step=step, context={
                'form': form,
            })
        else:
            self.update_history(step=step, form=form)
            self.after_process_step(step=step)
            next_step = self.get_next_step(current_step=step)
            return self.redirect_to_step(step=next_step)

    def update_history(self, step=None, form=None):
        self.storage.history.append_item({
            'step': step,
            'form_data': getattr(form, 'cleaned_data', None),
            'form_files': getattr(form, 'files', None),
        })

    def after_process_step(self, step=None):
        pass

    def get_next_step(self, current_step=None):
        pass

    def get_view_name(self):
        return getattr(self, 'view_name')

    def redirect_to_step(self, step=None):
        redirect(self.get_view_name, step=step)
