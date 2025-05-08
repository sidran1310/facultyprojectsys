import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile, Project, Application

# Simple helper to add 'required' CSS class or attribute if needed by frontend
# class RequiredFieldMixin:
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             if field.required:
#                 field.widget.attrs.setdefault('required', True) # HTML5 required
#                 # Or add a class:
#                 # current_class = field.widget.attrs.get('class', '')
#                 # field.widget.attrs['class'] = f'{current_class} required-field'.strip()


class CustomUserCreationForm(UserCreationForm):
    BRANCH_CHOICES = [
        ('CS', 'CS – Computer Science'),
        ('AI', 'AI – Artificial Intelligence'),
        ('ECE', 'ECE – Electrical and Communication Engineering'),
        ('ECM', 'ECM – Electronics and Computational Engineering'),
        ('CE', 'CE – Civil Engineering'),
        ('ME', 'ME – Mechanical Engineering'),
        ('CB', 'CB – Computational Biology'),
        ('BT', 'BT – Biotechnology'),
        ('CM', 'CM – Computational Mathematics'),
    ]

    branch = forms.ChoiceField(choices=BRANCH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}))

    # Fields for Profile, depending on inferred user type    branch = forms.CharField(max_length=50, required=False, label="Academic Branch (e.g., CS, ECE)",
    widget=forms.TextInput(attrs={'class': 'form-control'})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'name') # Password handled by UserCreationForm

    # Apply Bootstrap classes to password fields inherited from UserCreationForm
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
        self.fields['password1'].label = "Password"
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
        self.fields['password2'].label = "Confirm Password"
        for field in self.fields.values():
             field.widget.attrs.pop('autofocus', None) # Remove default autofocus


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        # Basic check for existing user
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Determine usertype based on email BEFORE saving user
        email = self.cleaned_data.get('email')
        match = re.search(r'\d{3}@', email)
        user.usertype = 'student' if match else 'professor'

        if commit:
            user.save()
            # Create or update Profile
            profile, created = Profile.objects.get_or_create(user=user)
            if user.usertype == 'student':
                profile.branch = self.cleaned_data.get('branch', '')
            else: # Professor
                profile.branch = None

            profile.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control', 'autocomplete': 'email'}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}))


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'status', 'category', 'branch']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['statementofinterest','resume']
        widgets = {
            'statementofinterest': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Explain why you are interested in this project and what skills you bring.'}),
        }
        labels = {
            'statementofinterest': 'Statement of Interest'
        }
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email'] # Email might be read-only depending on policy
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': True}), # Make email readonly
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally make email readonly if policy dictates
        self.fields['email'].disabled = True
        self.fields['email'].help_text = "Email cannot be changed."


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['academicdetails', 'branch']
        widgets = {
            'academicdetails': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfessorProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['facultyinformation']
        widgets = {
            'facultyinformation': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }