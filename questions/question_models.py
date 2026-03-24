from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms

class Question_DB(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE, null=True)
    qno = models.AutoField(primary_key=True)
    question = models.CharField(max_length=100, blank=True)
    question_image = models.ImageField(upload_to='question_media', blank=True, null=True)
    optionA = models.CharField(max_length=100, blank=True)
    optionA_image = models.ImageField(upload_to='question_media', blank=True, null=True)
    optionB = models.CharField(max_length=100, blank=True)
    optionB_image = models.ImageField(upload_to='question_media', blank=True, null=True)
    optionC = models.CharField(max_length=100, blank=True)
    optionC_image = models.ImageField(upload_to='question_media', blank=True, null=True)
    optionD = models.CharField(max_length=100, blank=True)
    optionD_image = models.ImageField(upload_to='question_media', blank=True, null=True)
    answer = models.CharField(max_length=200)
    max_marks = models.IntegerField(default=0)

    def __str__(self):
        question_title = self.question or f'Question No.{self.qno}'
        return f'Question No.{self.qno}: {question_title} \t\t Options: \nA. {self.optionA} \nB.{self.optionB} \nC.{self.optionC} \nD.{self.optionD} '


class QForm(ModelForm):
    class Meta:
        model = Question_DB
        fields = '__all__'
        exclude = ['qno', 'professor']
        widgets = {
            'question': forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Type the question text'}),
            'question_image': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'optionA': forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Type option A'}),
            'optionA_image': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'optionB': forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Type option B'}),
            'optionB_image': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'optionC': forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Type option C'}),
            'optionC_image': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'optionD': forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Type option D'}),
            'optionD_image': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'answer': forms.TextInput(attrs = {'class':'form-control', 'placeholder': 'Use A/B/C/D or exact option text'}),
            'max_marks': forms.NumberInput(attrs = {'class':'form-control', 'placeholder': 'Enter maximum marks'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_pairs = [
            ('question', 'question_image', 'question'),
            ('optionA', 'optionA_image', 'option A'),
            ('optionB', 'optionB_image', 'option B'),
            ('optionC', 'optionC_image', 'option C'),
            ('optionD', 'optionD_image', 'option D'),
        ]

        for text_field, image_field, label in required_pairs:
            text_value = (cleaned_data.get(text_field) or '').strip()
            image_value = cleaned_data.get(image_field)
            if not text_value and not image_value:
                self.add_error(text_field, f'Add text or upload an image for {label}.')

        answer = (cleaned_data.get('answer') or '').strip()
        if answer:
            answer_upper = answer.upper()
            if answer_upper not in {'A', 'B', 'C', 'D'}:
                option_texts = {
                    (cleaned_data.get('optionA') or '').strip().lower(),
                    (cleaned_data.get('optionB') or '').strip().lower(),
                    (cleaned_data.get('optionC') or '').strip().lower(),
                    (cleaned_data.get('optionD') or '').strip().lower(),
                }
                option_texts.discard('')
                if answer.lower() not in option_texts:
                    self.add_error('answer', 'Use A/B/C/D or enter the exact option text.')

        return cleaned_data
