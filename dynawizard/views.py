from django.shortcuts import render, redirect
from django.views.generic.base import View


class DynaWizard(View):

    http_method_names = ['get', 'post', 'options']

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
            next_step = self.get_next_step(current_step=step)
            return self.redirect_to_step(step=next_step)

    def get_next_step(self, current_step=None):
        pass

    def redirect_to_step(self, step=None):
        redirect(self.base_url, step=step)
