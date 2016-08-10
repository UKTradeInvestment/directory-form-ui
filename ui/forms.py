from django import forms
from django.forms.utils import ErrorList


class ContactForm(forms.Form):
    company_name = forms.CharField(required=True, max_length=255)
    contact_name = forms.CharField(required=True, max_length=255)
    email_address1 = forms.EmailField(required=True, max_length=255)
    email_address2 = forms.EmailField(required=True, max_length=255)
    phone_number = forms.CharField(required=False, max_length=255)
    website = forms.CharField(required=True, max_length=255)
    exporting = forms.ChoiceField(
        required=True,
        choices=[('True', 'True'), ('False', 'False')],
        widget=forms.RadioSelect(),
    )
    agree_terms = forms.BooleanField(required=True)
    opt_in = forms.BooleanField(required=False)


    marketing_source = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Please select an option'),
            ('Social media', 'Social media'),
            ('Print or online news', 'Print or online news'),
            ('Bank', 'Bank (please specify which bank, below)'),
            ('Department for International Trade', 'Department for International Trade'),
            ('HMRC email', 'HMRC email'),
            ("Exporting is GREAT website", "Exporting is GREAT website"),
            ("Trade association", "Trade association"),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    other_source_bank = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'cols': 50}))

    def clean(self):
        cleaned_data = super().clean()
        email1 = cleaned_data.get("email_address1")
        email2 = cleaned_data.get("email_address2")

        if email1 and email2 and email1.lower() != email2.lower():
            for field in ['email_address1', 'email_address2']:
                if field not in self._errors:
                    self._errors[field] = ErrorList()
                self._errors[field].append(
                    'Email addresses do not match',
                )
        return cleaned_data
