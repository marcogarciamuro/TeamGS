from django import forms
from dal import autocomplete


class TeamSearch(forms.Form):
    team_query = forms.CharField(
        widget=autocomplete.ListSelect2(
            url='/nba_team_autocomplete/',
            attrs={
                'size': 15,
                'data-placeholder': 'Team Name',
                'class': 'form-control',
                'data-selected-html': True,
                'data-result-html': True,
            }
        ),
        label=''
    )
