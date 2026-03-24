from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from .question_models import Question_DB
from django import forms
from examProject.text_utils import normalize_title_case

class Question_Paper(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    qPaperTitle = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question_DB)

    def __str__(self):
        return self.qPaperTitle


class QPForm(ModelForm):
    def __init__(self,professor,*args,**kwargs):
        super (QPForm,self ).__init__(*args,**kwargs) 
        self.fields['questions'].queryset = Question_DB.objects.filter(professor=professor)

    def clean_qPaperTitle(self):
        return normalize_title_case(self.cleaned_data.get('qPaperTitle'))

    class Meta:
        model = Question_Paper
        fields = '__all__'
        exclude = ['professor']
        widgets = {
            'qPaperTitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter question paper title',
            }),
            'questions': forms.SelectMultiple(attrs={
                'class': 'form-control question-paper-select',
                'size': 10,
            }),
        }
