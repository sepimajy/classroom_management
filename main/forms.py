from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Classroom, Assignment, Submission, Exam, Question, Message, Profile
import re
from datetime import timedelta

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    secret_code = forms.CharField(required=False, help_text='Enter secret code for teacher access (optional).')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'secret_code']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Classroom Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Classroom Description', 'rows': 3}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'file', 'due_date', 'allow_late_submission']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignment Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Assignment Description', 'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'allow_late_submission': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'start_time', 'end_time', 'duration']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Exam Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Exam Description', 'rows': 4}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 02:30:00 for 2 hours 30 minutes'}),
        }
    
    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if not isinstance(duration, str):
            duration = str(duration)
        duration = duration.strip()  # Remove leading/trailing whitespaces
        
        pattern = r'^(\d{1,2}):([0-5]\d):([0-5]\d)$'  # Allow 1 or 2 digits for hours
        
        if not re.match(pattern, duration):
            raise forms.ValidationError('Duration must be in HH:MM:SS format.')
        
        # Convert to timedelta
        try:
            hours, minutes, seconds = map(int, duration.split(':'))
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except ValueError:
            raise forms.ValidationError('Invalid duration format.')
        


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'image']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Question Text', 'rows': 3}),
            'option_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}),
            'correct_option': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'content', 'file']  
        widgets = {
            'receiver': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Type your message here...', 'rows': 3}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class JoinClassroomForm(forms.Form):
    code = forms.UUIDField(help_text='Enter the unique classroom code.')



class NumberOfQuestionsForm(forms.Form):
    number_of_questions = forms.IntegerField(
        label='Number of Questions',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of questions'})
    )