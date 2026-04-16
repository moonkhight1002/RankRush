from django import forms
from .models import StudentInfo
from django.contrib.auth.models import User
from examProject.text_utils import normalize_title_case

class StudentForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=120,
        required=True,
        error_messages={'required': 'Full name is required.'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
    )

    def clean_full_name(self):
        return normalize_title_case(self.cleaned_data.get('full_name'))
    
    class Meta():
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs = {'id':'passwordfield','class':'form-control', 'placeholder': 'Password'}),
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
