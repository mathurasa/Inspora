"""
Forms for accounts app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import User, Team, TeamMembership

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with additional fields."""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Customize help text
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['email'].help_text = 'Required. Enter a valid email address.'


class UserProfileEditForm(forms.ModelForm):
    """Enhanced form for editing user profile information."""
    
    # Additional fields for better user experience
    confirm_email = forms.EmailField(
        label='Confirm Email',
        help_text='Please confirm your email address'
    )
    
    # Password change fields
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Enter your current password to change it'
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Leave blank if you don\'t want to change your password'
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Enter the same password as before, for verification'
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'avatar', 'bio', 'phone_number',
            'job_title', 'department', 'employee_id', 'timezone', 'language',
            'email_notifications', 'push_notifications'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Engineer, Project Manager'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Engineering, Marketing, Sales'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employee ID (optional)'
            }),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial value for confirm email
        if self.instance and self.instance.email:
            self.fields['confirm_email'].initial = self.instance.email
        
        # Add choices for timezone and language
        self.fields['timezone'].choices = [
            ('UTC', 'UTC'),
            ('America/New_York', 'Eastern Time'),
            ('America/Chicago', 'Central Time'),
            ('America/Denver', 'Mountain Time'),
            ('America/Los_Angeles', 'Pacific Time'),
            ('Europe/London', 'London'),
            ('Europe/Paris', 'Paris'),
            ('Asia/Tokyo', 'Tokyo'),
            ('Asia/Shanghai', 'Shanghai'),
            ('Australia/Sydney', 'Sydney'),
        ]
        
        self.fields['language'].choices = [
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ru', 'Russian'),
            ('zh', 'Chinese'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
        ]
        
        # Add Bootstrap classes to checkboxes
        self.fields['email_notifications'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['push_notifications'].widget.attrs.update({'class': 'form-check-input'})
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        
        # Check if emails match
        if email and confirm_email and email != confirm_email:
            raise forms.ValidationError('Email addresses do not match.')
        
        # Check if email is already taken by another user
        if email and email != self.instance.email:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This email address is already in use.')
        
        # Validate password change
        current_password = cleaned_data.get('current_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 or new_password2:
            if not current_password:
                raise forms.ValidationError('Current password is required to change your password.')
            
            if not self.instance.check_password(current_password):
                raise forms.ValidationError('Current password is incorrect.')
            
            if new_password1 != new_password2:
                raise forms.ValidationError('New passwords do not match.')
            
            if len(new_password1) < 8:
                raise forms.ValidationError('New password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Handle password change
        if self.cleaned_data.get('new_password1'):
            user.set_password(self.cleaned_data['new_password1'])
        
        if commit:
            user.save()
        return user


class TeamForm(forms.ModelForm):
    """Form for creating and editing teams."""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'logo', 'is_public', 'allow_guest_access', 'max_members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter team name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your team...'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_guest_access': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_members': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 1000
            }),
        }


class TeamMembershipForm(forms.ModelForm):
    """Form for managing team memberships."""
    
    class Meta:
        model = TeamMembership
        fields = ['user', 'role', 'is_active']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users to only show active users
        self.fields['user'].queryset = User.objects.filter(is_active=True)


class PricingRegistrationForm(forms.Form):
    """Form for pricing page registration."""
    
    PLAN_CHOICES = [
        ('free', 'Free Plan'),
        ('starter', 'Starter Plan'),
        ('professional', 'Professional Plan'),
        ('enterprise', 'Enterprise Plan'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    company = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name (optional)'
        })
    )
    plan = forms.ChoiceField(
        choices=PLAN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us about your needs...'
        }),
        required=False
    )
