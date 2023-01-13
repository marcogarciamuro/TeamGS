from django import forms
from dal import autocomplete


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
    # Widget configuation for autocomplete
    # team_query = forms.CharField(
    #     widget=autocomplete.ListSelect2(
    #         url='/nba_team_autocomplete/',
    #         attrs={
    #             'size': 15,
    #             'data-placeholder': 'Team Name',
    #             'class': 'form-control',
    #             'data-selected-html': True,
    #             'data-result-html': True,
    #         }
    #     ),
    #     label=''
    # )
