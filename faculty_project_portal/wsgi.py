"""
WSGI config for faculty_project_portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Make sure this matches your project's settings file path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faculty_project_portal.settings')

application = get_wsgi_application()