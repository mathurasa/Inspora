from django import forms
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import UserProfile # Added import for UserProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user creation form with better UX and validation."""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make email required
        self.fields['email'].required = True
        
        # Add Bootstrap classes and placeholders
        field_attrs = {
            'username': {
                'class': 'form-control',
                'placeholder': 'Choose a unique username',
                'autocomplete': 'username'
            },
            'email': {
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'autocomplete': 'email'
            },
            'first_name': {
                'class': 'form-control',
                'placeholder': 'Enter your first name',
                'autocomplete': 'given-name'
            },
            'last_name': {
                'class': 'form-control',
                'placeholder': 'Enter your last name',
                'autocomplete': 'family-name'
            },
            'password1': {
                'class': 'form-control',
                'placeholder': 'Create a strong password',
                'autocomplete': 'new-password'
            },
            'password2': {
                'class': 'form-control',
                'placeholder': 'Confirm your password',
                'autocomplete': 'new-password'
            }
        }
        
        # Apply attributes to each field
        for field_name, attrs in field_attrs.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(attrs)
    
    def clean_email(self):
        """Enhanced email validation."""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    'This email is already registered. Please use a different email or sign in to your existing account.'
                )
            
            # Basic email format validation
            if not '@' in email or not '.' in email:
                raise forms.ValidationError('Please enter a valid email address.')
            
            # Check for common disposable email domains
            disposable_domains = ['10minutemail.com', 'tempmail.org', 'guerrillamail.com']
            domain = email.split('@')[1].lower()
            if domain in disposable_domains:
                raise forms.ValidationError('Please use a valid email address, not a temporary one.')
        
        return email
    
    def clean_username(self):
        """Enhanced username validation."""
        username = self.cleaned_data.get('username')
        if username:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    'This username is already taken. Please choose a different one.'
                )
            
            # Username format validation
            if len(username) < 3:
                raise forms.ValidationError('Username must be at least 3 characters long.')
            
            if len(username) > 30:
                raise forms.ValidationError('Username must be 30 characters or less.')
            
            # Check for valid characters
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                raise forms.ValidationError(
                    'Username can only contain letters, numbers, hyphens, and underscores.'
                )
        
        return username
    
    def clean_password1(self):
        """Enhanced password validation."""
        password = self.cleaned_data.get('password1')
        if password:
            # Check password length
            if len(password) < 8:
                raise forms.ValidationError(
                    'Password must be at least 8 characters long.'
                )
            
            # Check for common weak passwords
            weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
            if password.lower() in weak_passwords:
                raise forms.ValidationError(
                    'This password is too common. Please choose a stronger password.'
                )
            
            # Check password complexity
            if not any(c.isupper() for c in password):
                raise forms.ValidationError(
                    'Password must contain at least one uppercase letter.'
                )
            
            if not any(c.islower() for c in password):
                raise forms.ValidationError(
                    'Password must contain at least one lowercase letter.'
                )
            
            if not any(c.isdigit() for c in password):
                raise forms.ValidationError(
                    'Password must contain at least one number.'
                )
        
        return password
    
    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    'Passwords do not match. Please make sure both passwords are identical.'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with enhanced error handling."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Ensure email is properly set
        if not user.email:
            raise forms.ValidationError('Email is required.')
        
        if commit:
            try:
                user.save()
                print(f"User {user.username} created successfully")
            except Exception as e:
                print(f"Error saving user: {e}")
                raise forms.ValidationError('There was an error creating your account. Please try again.')
        
        return user


class PricingRegistrationForm(CustomUserCreationForm):
    """
    Enhanced registration form with pricing plan selection and additional fields.
    """
    # Plan selection
    selected_plan = forms.ChoiceField(
        choices=[
            ('free', 'Free Plan'),
            ('starter', 'Starter Plan'),
            ('professional', 'Professional Plan'),
            ('enterprise', 'Enterprise Plan'),
        ],
        widget=forms.RadioSelect,
        initial='free',
        help_text='Choose your plan to get started'
    )
    
    billing_cycle = forms.ChoiceField(
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly (Save 20%)'),
        ],
        initial='monthly',
        widget=forms.RadioSelect
    )
    
    # Company information
    company_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your company name'
        })
    )
    
    company_size = forms.ChoiceField(
        choices=[
            ('', 'Select company size'),
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('500+', '500+ employees'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    industry = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Technology, Healthcare, Finance'
        })
    )
    
    # Professional details
    job_title = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Project Manager, Developer'
        })
    )
    
    years_experience = forms.ChoiceField(
        choices=[
            ('', 'Select experience level'),
            ('0-1', '0-1 years'),
            ('2-5', '2-5 years'),
            ('6-10', '6-10 years'),
            ('11-15', '11-15 years'),
            ('15+', '15+ years'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Contact preferences
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        })
    )
    
    preferred_contact_method = forms.ChoiceField(
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('slack', 'Slack'),
            ('teams', 'Microsoft Teams'),
        ],
        initial='email',
        widget=forms.RadioSelect
    )
    
    # Marketing and terms
    marketing_consent = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Payment Information (for paid plans)
    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'data-stripe': 'number'
        })
    )
    
    card_expiry = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'data-stripe': 'exp'
        })
    )
    
    card_cvc = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'data-stripe': 'cvc'
        })
    )
    
    card_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name on card'
        })
    )
    
    billing_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Billing address'
        })
    )
    
    billing_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    billing_state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province'
        })
    )
    
    billing_zip = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP/Postal code'
        })
    )
    
    billing_country = forms.ChoiceField(
        choices=[
            ('', 'Select country'),
            ('US', 'United States'),
            ('CA', 'Canada'),
            ('GB', 'United Kingdom'),
            ('AU', 'Australia'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('JP', 'Japan'),
            ('IN', 'India'),
            ('BR', 'Brazil'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to existing fields
        for field_name, field in self.fields.items():
            if field_name not in ['selected_plan', 'billing_cycle', 'preferred_contact_method', 'marketing_consent', 'terms_accepted']:
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs.update({'class': 'form-control'})
                else:
                    field.widget.attrs = {'class': 'form-control'}
    
    def clean(self):
        cleaned_data = super().clean()
        selected_plan = cleaned_data.get('selected_plan')
        billing_cycle = cleaned_data.get('billing_cycle')
        
        # Validate plan-specific requirements
        if selected_plan in ['starter', 'professional', 'enterprise']:
            company_name = cleaned_data.get('company_name')
            if not company_name:
                raise forms.ValidationError(
                    f"Company name is required for {selected_plan.title()} plan."
                )
            
            # Validate payment information for paid plans
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvc = cleaned_data.get('card_cvc')
            card_name = cleaned_data.get('card_name')
            
            if not all([card_number, card_expiry, card_cvc, card_name]):
                raise forms.ValidationError(
                    "Payment information is required for paid plans."
                )
            
            # Validate card number format (basic validation)
            if card_number and len(card_number.replace(' ', '')) < 13:
                raise forms.ValidationError(
                    "Please enter a valid card number."
                )
            
            # Validate expiry date format
            if card_expiry and not re.match(r'^\d{2}/\d{2}$', card_expiry):
                raise forms.ValidationError(
                    "Please enter expiry date in MM/YY format."
                )
            
            # Validate CVC
            if card_cvc and len(card_cvc) < 3:
                raise forms.ValidationError(
                    "Please enter a valid CVC."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.company_name = self.cleaned_data.get('company_name', '')
            profile.company_size = self.cleaned_data.get('company_size', '')
            profile.industry = self.cleaned_data.get('industry', '')
            profile.years_experience = self.cleaned_data.get('years_experience', '0')
            profile.preferred_contact_method = self.cleaned_data.get('preferred_contact_method', 'email')
            profile.marketing_consent = self.cleaned_data.get('marketing_consent', False)
            profile.save()
            
            # Update user fields
            user.job_title = self.cleaned_data.get('job_title', '')
            user.phone_number = self.cleaned_data.get('phone_number', '')
            user.save()
            
            # Create subscription (this will be handled by the view)
        
        return user
