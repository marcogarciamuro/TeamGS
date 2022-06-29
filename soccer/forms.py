from django import forms
from django.contrib.auth.models import User

class TeamSearch(forms.Form):
    team_query = forms.CharField(widget=forms.TextInput(
        attrs={
            'size': '30', 
            'placeholder': 'Team Search', 
            'margin': "auto", 
            'max-width': "300px",
            # "class": 'basicAutoComplete',
            # "data-url": "/domain/teams-autocomplete"
        }), 
        label=""
    )
    # style="margin:auto;max-width:300px"