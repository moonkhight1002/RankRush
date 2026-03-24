from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from datetime import datetime
from .questionpaper_models import Question_Paper
from django import forms
from examProject.text_utils import normalize_title_case

class Exam_Model(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    total_marks = models.IntegerField()
    question_paper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, related_name='exams')
    start_time = models.DateTimeField(default=datetime.now())
    end_time = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.name


class ExamForm(ModelForm):
    def __init__(self,professor,*args,**kwargs):
        super (ExamForm,self ).__init__(*args,**kwargs) 
        self.fields['question_paper'].queryset = Question_Paper.objects.filter(professor=professor)
        self.fields['question_paper'].empty_label = 'Click to select question paper'

    def clean_name(self):
        return normalize_title_case(self.cleaned_data.get('name'))

    class Meta:
        model = Exam_Model
        fields = '__all__'
        exclude = ['professor']
        widgets = {
            'name': forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Enter exam name'}),
            'question_paper': forms.Select(attrs={'class': 'form-control schedule-select'}),
            'total_marks' : forms.NumberInput(attrs = {'class':'form-control', 'placeholder': 'Enter total marks'}),
            'start_time': forms.DateTimeInput(attrs = {'class':'form-control schedule-datetime'}),
            'end_time': forms.DateTimeInput(attrs = {'class':'form-control schedule-datetime'})
        }
