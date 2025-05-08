from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def user_type_required(user_type):
    #Decorator for views that requires the logged-in user to have a specific usertype.
    def decorator(view_func):
        @wraps(view_func)
        @login_required # Ensures user is logged in first
        def _wrapped_view(request, *args, **kwargs):
            # Check if user object has 'usertype' attribute (it should with our custom model)
            if not hasattr(request.user, 'usertype') or request.user.usertype != user_type:
                messages.error(request, f"Access Denied: This page is restricted to {user_type.capitalize()} users.")
                # Redirect based on actual user type, or home if unknown/unexpected
                if hasattr(request.user, 'usertype'):
                    if request.user.usertype == 'student':
                        return redirect('student_dashboard')
                    elif request.user.usertype == 'professor':
                        return redirect('professor_dashboard')
                    else:
                        return redirect('home') # Fallback for unexpected types
                else:
                    # If usertype attribute is missing (shouldn't happen with correct setup)
                    return redirect('home')
            # If user type matches, execute the original view function
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

student_required = user_type_required('student')
professor_required = user_type_required('professor')