from django import forms
from django.contrib.auth.models import User
from .models import FacultyInfo
from examProject.text_utils import normalize_title_case


class FacultyForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=120,
        required=True,
        error_messages={'required': 'Full name is required.'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_full_name(self):
        return normalize_title_case(self.cleaned_data.get('full_name'))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class FacultyInfoForm(forms.ModelForm):
    def clean_subject(self):
        return normalize_title_case(self.cleaned_data.get('subject'))

    class Meta:
        model = FacultyInfo
        fields = ['address', 'subject', 'picture']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject You Teach'}),
        }
