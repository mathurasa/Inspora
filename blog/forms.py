from django import forms
from .models import Comment, Newsletter

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Write your comment here...'
        }),
        label='Comment'
    )
    
    class Meta:
        model = Comment
        fields = ['content']

class NewsletterForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        label='Email'
    )
    
    class Meta:
        model = Newsletter
        fields = ['email']
