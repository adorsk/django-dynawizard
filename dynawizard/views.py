import os
from django.shortcuts import render, redirect
from django.views.generic.base import View

from . import storage


class DynaWizard(View):
    key = 'dynawizard'
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
        return self.key

    def get_storage_name(self):
        return 'dynawizard.storage.session.SessionStorage'

    def get(self, request, step=None, **kwargs):
        if not step:
            step = self.get_initial_step()
        form = self.get_form_instance(request, step=step)
        return self.render_step(request, step=step, context={
            'form': form,
        })

    def get_initial_step(self):
        return 'start'

    def get_form_instance(self, request, step=None, form_args=None):
        form_instance = None
        form_class = self.get_form_class(step=step)
        if form_class:
            altered_form_args = self.get_altered_form_args(
                request=request, step=step, form_args=form_args)
            if altered_form_args:
                form_instance = form_class(*altered_form_args)
            else:
                form_instance = form_class()
        return form_instance

    def get_form_class(self, step=None):
        form_class = None
        return form_class

    def get_altered_form_args(self, request, step=None, form_args=None):
        return form_args

    def render_step(self, request, step=None, context={}):
        altered_context = self.alter_render_context(step=step, context=context)
        template_name = self.get_template_name_for_step(step=step)
        return render(request, template_name, context=altered_context)

    def alter_render_context(self, step=None, context={}):
        return context

    def get_template_name_for_step(self, step=None):
        return os.path.join(self.get_template_base_path(), step + '.html')

    def get_template_base_path(self):
        return self.key

    def post(self, request, step=None, **kwargs):
        if not step:
            step = self.get_initial_step()
        form = self.get_form_instance(request, step=step,
                                      form_args=[request.POST])
        if form and not form.is_valid():
            return self.render_step(request, step=step, context={
                'form': form,
            })
        else:
            history_item = {
                'form_data': getattr(form,'cleaned_data', None),
                'form_files': getattr(form, 'files', None),
                'step': step,
                'extra': {},
            }
            altered_history_item = self.get_altered_history_item(
                request, step=step, history_item=history_item)
            self.append_history_item(history_item=altered_history_item)
            next_step = self.get_next_step(current_step=step)
            self.before_redirect_to_next_step(current_step=step,
                                              next_step=next_step)
            return self.redirect_to_step(target_step=next_step)

    def get_altered_history_item(self, request, step=None, history_item=None):
        return history_item

    def append_history_item(self, history_item={}):
        self.storage.history.append_item({
            'step': history_item.get('step', None),
            'form_data': history_item.get('form_data', None),
            'form_files': history_item.get('form_files', None),
            'extra': history_item.get('extra', None),
        })

    def get_next_step(self, current_step=None):
        pass

    def before_redirect_to_next_step(self, current_step=None, next_step=None):
        pass

    def redirect_to_step(self, target_step=None):
        return redirect(self.get_view_name(), step=target_step)

    def get_view_name(self):
        return getattr(self, 'view_name')
