from django import forms

class EmailLoginForm(forms.Form):
    email = forms.EmailField()
