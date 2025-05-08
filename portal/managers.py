import re
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def determine_user_type(self, email):
        # Check if there are exactly three digits before the '@' symbol
        match = re.search(r'\d{3}@', email)
        if match:
            return 'student'
        else:
            return 'professor'

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not name:
            raise ValueError('The Name field must be set')

        email = self.normalize_email(email)
        usertype = self.determine_user_type(email)
        extra_fields.setdefault('usertype', usertype)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('usertype', 'professor') # Superusers are often staff/profs

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)