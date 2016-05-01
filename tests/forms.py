from django import forms


class TestForm(forms.Form):
    field1 = forms.CharField()
    field1_ = forms.CharField()
    bool1 = forms.BooleanField(required=False)
    date1 = forms.DateField(required=False)
