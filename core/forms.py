from django import forms
from django.contrib.auth.models import User


class JoinForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'First Name',
        }), label=''
    )
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Last Name',
        }), label=''
    )
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Username',
        }), label=''
    )
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'autocomplete': 'newpassword',
            'placeholder': 'Password'
        }), label=''
    )
    email = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Email',
        }), label=''
    )

    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        help_texts = {
            'username': None
        }


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Username',
        }), label=''
    )
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'placeholder': 'Password',
        }), label=''
    )
