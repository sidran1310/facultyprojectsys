from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager # Import the custom manager
from django.db.models import UniqueConstraint

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    # Use Django's auto ID as primary key conceptually representing userid
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    usertype = models.CharField(max_length=10, choices=[('student', 'Student'), ('professor', 'Professor')])

    is_staff = models.BooleanField(default=False) # Required for Django admin
    is_active = models.BooleanField(default=True) # Required for Django auth
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email' # Use email for login
    REQUIRED_FIELDS = ['name'] # Required fields when creating user via createsuperuser

    objects = CustomUserManager() # Assign the custom manager

    def __str__(self):
        return self.email

# Profile Model for additional details
class Profile(models.Model):
    # Use Django's auto ID as primary key
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Combined fields, view logic will determine which one is relevant based on usertype
    academicdetails = models.TextField(blank=True, null=True, verbose_name="Academic Details (Students)")
    facultyinformation = models.TextField(blank=True, null=True, verbose_name="Faculty Information (Professors)")
    branch = models.CharField(max_length=50, blank=True, null=True, verbose_name="Branch (Students)") # Student specific

    def __str__(self):
        return f"{self.user.name}'s Profile"

# Project Model
class Project(models.Model):
    # Use Django's auto ID as primary key conceptually representing projectid
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Ensure FK references User model, limit choices in forms/views
    professorid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects_led', limit_choices_to={'usertype': 'professor'}, db_column='professorid')
    # Store professor name denormalized for easier filtering as requested
    professorname = models.CharField(max_length=150)
    status_choices = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('InProgress', 'In Progress'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Open')
    category_choices = [
        ('Research', 'Research'),
        ('Development', 'Software Development'),
        ('Design', 'Design'),
        ('DataAnalysis', 'Data Analysis'),
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=category_choices, default='Other')
    branch_choices = [
        ('CS', 'Computer Science'),
        ('ECE', 'Electronics & Comm.'),
        ('ME', 'Mechanical Eng.'),
        ('CE', 'Civil Eng.'),
        ('EE', 'Electrical Eng.'),
        ('CH', 'Chemical Eng.'),
        ('AE', 'Aerospace Eng.'),
        ('BT', 'Biotechnology'),
        ('Multi', 'Multidisciplinary'),
    ]
    branch = models.CharField(max_length=5, choices=branch_choices, default='Multi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    # Automatically set professorname when saving
    def save(self, *args, **kwargs):
        # Ensure professorid exists before trying to access its name
        if self.professorid_id: # Check the foreign key ID directly
            try:
                # Fetch the related User object only if needed
                if not self.professorname or self.professorid.name != self.professorname:
                     # Avoid unnecessary DB hit if professorid object isn't loaded yet
                    prof = User.objects.get(pk=self.professorid_id)
                    self.professorname = prof.name
            except User.DoesNotExist:
                 self.professorname = "Unknown Professor" # Handle case where user might be deleted?
        else:
            self.professorname = "N/A" # Or handle as appropriate
        super().save(*args, **kwargs)

# Application Model
class Application(models.Model):
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    studentid = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'usertype': 'student'}, db_column='studentid')
    projectid = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='projectid', related_name='applications')
    statementofinterest = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    applicationdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.studentid.name} → {self.projectid.title}"

    class Meta:
        constraints = [
            UniqueConstraint(fields=['studentid', 'projectid'], name='unique_student_project_application')
        ]

    def __str__(self):
        # Use IDs directly to avoid extra DB queries in admin/shell if objects aren't loaded
        return f"Application by Student ID {self.studentid_id} for Project ID {self.projectid_id}"
from django.conf import settings

class Slot(models.Model):
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='booked_slots')
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time} by {self.professor.name}"
