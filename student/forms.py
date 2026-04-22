from django import forms
from django.core.exceptions import ValidationError
from .models import StudentInfo
from django.contrib.auth.models import User
from examProject.password_policy import (
    PASSWORD_REQUIREMENTS_TEXT,
    build_signup_password_widget_attrs,
    validate_signup_password,
)
from examProject.text_utils import normalize_title_case
from studentPreferences.auth_identifier import (
    build_auth_identifier_username,
    get_auth_identifier_settings,
    strip_auth_identifier_affix,
)

class StudentForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=120,
        required=True,
        error_messages={'required': 'Full name is required.'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
    )
    password = forms.CharField(
        help_text=PASSWORD_REQUIREMENTS_TEXT,
        error_messages={'required': 'Password is required.'},
        widget=forms.PasswordInput(
            attrs=build_signup_password_widget_attrs(
                {'id': 'passwordfield', 'class': 'form-control', 'placeholder': 'Password'}
            )
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_identifier_settings = get_auth_identifier_settings()
        if self.auth_identifier_settings.username_mode == self.auth_identifier_settings.MODE_EMAIL_PREFIX:
            self.fields['username'].required = False
            self.fields['username'].widget = forms.HiddenInput()

    def clean_full_name(self):
        return normalize_title_case(self.cleaned_data.get('full_name'))

    def clean_username(self):
        raw_username = strip_auth_identifier_affix(self.cleaned_data.get('username'))
        email_value = self.data.get('email') or self.cleaned_data.get('email')
        if self.auth_identifier_settings.username_mode == self.auth_identifier_settings.MODE_EMAIL_PREFIX:
            username_value = build_auth_identifier_username(raw_username, email=email_value)
            if not username_value:
                raise ValidationError('Enter a valid email address so we can create your username.')
            return username_value
        if not raw_username:
            return raw_username
        if not raw_username.isalnum():
            raise ValidationError('Username should only contain alphanumeric characters.')
        return build_auth_identifier_username(raw_username)

    def clean_password(self):
        return validate_signup_password(self.cleaned_data.get('password'))
    
    class Meta():
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'email' : forms.EmailInput(attrs = {'id':'emailfield','class':'form-control', 'placeholder': 'Email Address'}),
            'username' : forms.TextInput(attrs = {'id':'usernamefield','class':'form-control', 'placeholder': 'Username'})
        }

class StudentInfoForm(forms.ModelForm):
    def clean_stream(self):
        return normalize_title_case(self.cleaned_data.get('stream'))

    class Meta():
        model = StudentInfo
        fields = ['address','stream','picture']
        widgets = {
            'address': forms.Textarea(attrs = {'class':'form-control'}),
            'stream' : forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Stream / Course'})
        }
