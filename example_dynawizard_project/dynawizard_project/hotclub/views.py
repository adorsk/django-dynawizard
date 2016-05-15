import os
import copy

from django import forms
from django.shortcuts import render

from dynawizard.views import DynaWizard


class BandForm(forms.Form):
    band_name = forms.CharField()

class InstrumentForm(forms.Form):
    instrument = forms.ChoiceField(choices=[
        ('GUITAR', 'Guitar',),
        ('VIOLIN', 'Violin',),
    ])

class GuitaristForm(forms.Form):
    musician = forms.ChoiceField(choices=[
        ('django', 'Django Reinhardt'),
        ('dorado', 'Dorado Schmitt'),
    ])

class ViolinistForm(forms.Form):
    musician = forms.ChoiceField(choices=[
        ('stephane', 'Stephane Grapelli'),
        ('pierre', 'Pierre Blanchard'),
    ])

musician_forms = {
    'GUITAR': GuitaristForm,
    'VIOLIN': ViolinistForm,
}

class HotClubWizard(DynaWizard):
    key = 'hotclub_wizard'
    view_name = 'hotclub_wizard'

    def get_template_base_path(self):
        return os.path.join('hotclub', self.key)

    def get_form_class(self, step=None):
        if step == 'band':
            return BandForm
        elif step == 'instrument':
            return InstrumentForm
        elif step == 'musician':
            prev_history_item = self.storage.history[-1]
            instrument = prev_history_item['form_data']['instrument']
            return musician_forms[instrument]

    def get_altered_form_args(self, request, step=None, form_args=None):
        altered_form_args = form_args
        if request.method == 'GET' and step == 'band':
            history_item = self.storage.history.load_bookmarked_item(key=step)
            if history_item:
                altered_form_args = [
                    history_item['form_data'],
                    history_item['form_files'],
                ]
        return altered_form_args

    def get_initial_step(self):
        return 'band'

    def get_altered_history_item(self, request, step=None, history_item=None):
        altered_history_item = copy.copy(history_item)
        if step == 'band':
            altered_history_item['extra'] = {
                'next_step': request.POST.get('next_step'),
            }
        return altered_history_item

    def get_next_step(self, current_step=None):
        if current_step == 'band':
            return self.storage.history[-1]['extra']['next_step']
        elif current_step == 'instrument':
            return 'musician'
        elif current_step == 'musician':
            return 'band'

    def before_redirect_to_next_step(self, current_step=None, next_step=None):
        if current_step == 'band':
            item_idx = len(self.storage.history) - 1
            self.storage.history.add_bookmark(key=current_step,
                                              item_idx=item_idx)

