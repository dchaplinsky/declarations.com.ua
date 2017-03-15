from django import forms


class UserProfileForm(forms.Form):
    email = forms.EmailField(label='E-mail', max_length=100)
