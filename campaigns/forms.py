from django import forms

from .models import Campaign, Invitee
from django.utils import timezone


class InviteeCSVUploadForm(forms.Form):

    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV containing name, phone and email."
    )

    def clean_csv_file(self):

        file = self.cleaned_data["csv_file"]

        if not file.name.lower().endswith(".csv"):
            raise forms.ValidationError(
                "Only CSV files are allowed."
            )

        max_size = 5 * 1024 * 1024

        if file.size > max_size:
            raise forms.ValidationError(
                "CSV file must be smaller than 5 MB."
            )

        return file





class CampaignCreateForm(forms.ModelForm):

    invitees = forms.ModelMultipleChoiceField(
        queryset=Invitee.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    select_all = forms.BooleanField(
        required=False,
        label="Select all invitees"
    )

    class Meta:

        model = Campaign

        fields = [
            "name",
            "event_name",
            "event_date",
            "event_location",
            "objective",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "event_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "event_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "event_location": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "objective": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),
        }

    def clean_event_date(self):

        event_date = self.cleaned_data["event_date"]

        if event_date < timezone.localdate():
            raise forms.ValidationError(
                "Event date cannot be in the past."
            )

        return event_date