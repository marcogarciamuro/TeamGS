from django import forms
from django.contrib.auth.models import User


class TeamSearch(forms.Form):
    team_query = forms.CharField(widget=forms.TextInput(
        attrs={
            'size': '15',
            'placeholder': 'Team Search',
            'margin': 'auto',
            'class': 'form-control'
        }),
        label=""
    )
