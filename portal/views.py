from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q, Count # For filtering and aggregation
from django.http import HttpResponseForbidden # For permission errors
from .forms import (
    CustomUserCreationForm, ProjectForm, ApplicationForm,
    UserProfileForm, StudentProfileForm, ProfessorProfileForm
)
from .models import User, Profile, Project, Application
from .decorators import student_required, professor_required

# --- Views ---

def home_view(request):
    # Optionally pass some featured projects or stats to the homepage
    featured_projects = Project.objects.filter(status='Open').order_by('-created_at')[:3]
    context = {
        'featured_projects': featured_projects
    }
    return render(request, 'portal/home.html', context)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Profile is also created/updated in form's save method
            # Log the user in directly after successful registration
            login(request, user, backend='django.contrib.auth.backends.ModelBackend') # Explicitly specify backend
            messages.success(request, f'Registration successful! Welcome, {user.name}.')
            return redirect('dashboard_redirect')
        else:
            # Form is invalid, add general error message
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# Login view is handled by Django's built-in auth_views.LoginView configured in portal/urls.py

@login_required
def dashboard_redirect_view(request):
    #Redirects users to their specific dashboard after login.
    if hasattr(request.user, 'usertype'):
        if request.user.usertype == 'student':
            return redirect('student_dashboard')
        elif request.user.usertype == 'professor':
            return redirect('professor_dashboard')
        else:
            # Handle unexpected user type
            messages.warning(request, 'User type not recognized. Please contact support.')
            logout(request)
            return redirect('home')
    else:
        # Handle case where user object might not have usertype (shouldn't happen)
        messages.error(request, 'User profile incomplete. Logging out.')
        logout(request)
        return redirect('home')


@student_required
def student_dashboard_view(request):
    # Fetch recent applications or other relevant info
    recent_applications = Application.objects.filter(studentid=request.user).select_related('projectid').order_by('-applicationdate')[:5]
    open_projects_count = Project.objects.filter(status='Open').count()
    context = {
        'recent_applications': recent_applications,
        'open_projects_count': open_projects_count,
    }
    return render(request, 'portal/student_dashboard.html', context)

@professor_required
def professor_dashboard_view(request):
    # Fetch professor's projects and application counts
    professor_projects = Project.objects.filter(professorid=request.user).annotate(
        pending_applications_count=Count('applications', filter=Q(applications__status='Pending')),
        approved_applications_count=Count('applications', filter=Q(applications__status='Approved')),
    ).order_by('-created_at')
    total_pending = sum(p.pending_applications_count for p in professor_projects)
    context = {
        'projects': professor_projects,
        'total_pending': total_pending,
    }
    return render(request, 'portal/professor_dashboard.html', context)

@login_required # Accessible by both, but template adjusts actions
def project_list_view(request):
    # Start with active projects, professors might see their closed ones too?
    # For now, default to Open for everyone viewing the list.
    projects_query = Project.objects.all() # Get all first, then filter

    # Get distinct values for filters - optimize by querying only needed fields
    # Only include professors who actually have projects
    prof_ids_with_projects = Project.objects.values_list('professorid', flat=True).distinct()
    professors = User.objects.filter(usertype='professor', id__in=prof_ids_with_projects).order_by('name').values_list('name', flat=True)

    categories = Project.category_choices
    branches = Project.branch_choices
    statuses = Project.status_choices

    # --- Filtering ---
    filters = Q() # Start with an empty Q object

    # Default status filter (only show Open unless another status is specified)
    default_status_applied = False
    status_filter = request.GET.get('status', '')
    if status_filter:
        filters &= Q(status=status_filter)
        default_status_applied = True # A specific status was requested
    else:
        # Only apply default 'Open' if the user is NOT a professor
        # Or if the user IS a professor but didn't specify a status
        if not request.user.is_authenticated or request.user.usertype != 'professor':
             filters &= Q(status='Open')
             default_status_applied = True # Default applied


    query = request.GET.get('query', '').strip()
    professor_name_filter = request.GET.get('professorname', '')
    category_filter = request.GET.get('category', '')
    branch_filter = request.GET.get('branch', '')

    if query:
        filters &= Q(title__icontains=query)
    if professor_name_filter:
            filters &= Q(professorname__iexact=professor_name_filter)
    if category_filter:
        filters &= Q(category=category_filter)
    if branch_filter:
        filters &= Q(branch=branch_filter)

    # Apply all collected filters
    projects = projects_query.filter(filters).order_by('-created_at')


    context = {
        'projects': projects,
        'professors': professors,
        'categories': categories,
        'branches': branches,
        'statuses': statuses,
        'current_filters': request.GET, # Pass current filters back to template
        'default_status_applied': default_status_applied, # Help template show default status if applicable
    }
    return render(request, 'portal/project_list.html', context)

@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    has_applied = False
    application_status = None
    if request.user.usertype == 'student':
        # Use select_related to potentially optimize if accessing student/project later
        existing_application = Application.objects.filter(projectid=project, studentid=request.user).first()
        if existing_application:
            has_applied = True
            application_status = existing_application.status

    context = {
        'project': project,
        'has_applied': has_applied,
        'application_status': application_status,
    }
    return render(request, 'portal/project_detail.html', context)

@student_required
def apply_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, status='Open') # Can only apply to open projects

    # Check if already applied
    if Application.objects.filter(projectid=project, studentid=request.user).exists():
        messages.warning(request, 'You have already applied for this project.')
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.studentid = request.user
            application.projectid = project
            # application.status = 'Pending' # Default is Pending via model definition
            application.save()
            messages.success(request, f'Successfully applied for "{project.title}". Your application is pending review.')
            # TODO: Add notification logic here (e.g., using Django signals to email professor)
            return redirect('project_detail', project_id=project.id)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ApplicationForm()
        # Pre-fill profile info for context if needed, though not directly in form
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
             profile = None # Handle case where profile might be missing

    context = {
        'project': project,
        'form': form,
        'profile': profile # Pass profile for display purposes if needed
    }
    return render(request, 'portal/apply_form.html', context)

@professor_required
def add_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.professorid = request.user
            # professorname is set automatically on model save
            project.save()
            messages.success(request, f'Project "{project.title}" created successfully.')
            return redirect('professor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    return render(request, 'portal/project_form.html', {'form': form, 'form_title': 'Add New Project'})

@professor_required
def edit_project_view(request, project_id):
    # Ensure the professor owns the project they are trying to edit
    project = get_object_or_404(Project, pk=project_id, professorid=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            # professorid remains the same, professorname updates on save if needed
            form.save()
            messages.success(request, f'Project "{project.title}" updated successfully.')
            return redirect('professor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'portal/project_form.html', {'form': form, 'form_title': 'Edit Project'})

@professor_required
def delete_project_confirm_view(request, project_id):
    #Displays a confirmation page before deleting a project.
    project = get_object_or_404(Project, pk=project_id, professorid=request.user) # Ensure ownership
    application_count = project.applications.count()
    context = {
        'project': project,
        'application_count': application_count,
    }
    return render(request, 'portal/confirm_delete.html', context)


@professor_required
def delete_project_view(request, project_id):
    #Handles the actual deletion of a project after POST confirmation.
    project = get_object_or_404(Project, pk=project_id, professorid=request.user) # Ensure ownership
    if request.method == 'POST':
            project_title = project.title
            project.delete() # Deletes the project and related applications due to CASCADE
            messages.success(request, f'Project "{project_title}" and all related applications have been deleted.')
            return redirect('professor_dashboard')
    else:
        # If accessed via GET, redirect to the confirmation page or dashboard
        messages.warning(request, 'Use the confirmation page to delete projects.')
        return redirect('delete_project_confirm', project_id=project_id)


@professor_required
def view_project_applications_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, professorid=request.user) # Ensure ownership
    # Optimize query by selecting related student and profile data
    applications = Application.objects.filter(projectid=project)\
                                    .select_related('studentid', 'studentid__profile')\
                                    .order_by('applicationdate')
    context = {
        'project': project,
        'applications': applications,
    }
    return render(request, 'portal/view_applications.html', context)

@professor_required
def update_application_status_view(request, application_id, status):
    application = get_object_or_404(Application, pk=application_id)
    project = application.projectid

    # Security Check: Ensure the logged-in professor owns the project
    if project.professorid != request.user:
        # Use HttpResponseForbidden or raise PermissionDenied for clarity
        # return HttpResponseForbidden("You do not have permission to manage this application.")
        messages.error(request, 'You do not have permission to manage this application.')
        return redirect('professor_dashboard') # Or raise PermissionDenied

    valid_statuses = ['Approved', 'Denied', 'Pending'] # Allow reverting to Pending
    new_status = status.capitalize() # Ensure consistent casing

    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status update.')
    elif application.status != new_status:
        old_status = application.status
        application.status = new_status
        application.save()
        messages.success(request, f"Application for {application.studentid.name} updated from {old_status} to {new_status}.")
        # TODO: Add notification logic here (e.g., email student about the status change)
        # Example: send_application_status_update_email(application)
    else:
        messages.info(request, f"Application status is already {new_status}.")

    # Redirect back to the list of applications for the same project
    return redirect('view_project_applications', project_id=project.id)


@login_required
def profile_view(request):
    user = request.user
    # Use related name 'profile' defined in Profile model; handle potential DoesNotExist
    try:
        # profile = user.profile # Access via the related name
        profile = Profile.objects.get(user=user) # Or query explicitly
    except Profile.DoesNotExist:
        # This shouldn't happen if profile is created on signup, but handle defensively
        profile = None
        messages.warning(request, "Profile details not found. Please edit your profile to create them.")
        # Or automatically create one here: profile = Profile.objects.create(user=user)

    context = {
        # 'user': user, # 'user' is already available in templates by default when logged in
        'profile': profile
    }
    return render(request, 'portal/profile.html', context)

@login_required
def profile_edit_view(request):
    user = request.user
    # Ensure profile exists, create if not (defensive programming)
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        messages.info(request, "Created your profile details. Please review and save.")

    if request.method == 'POST':
        # Pass instance to update existing user/profile
        user_form = UserProfileForm(request.POST, instance=user)
        if user.usertype == 'student':
            profile_form = StudentProfileForm(request.POST, instance=profile)
        else: # professor
            profile_form = ProfessorProfileForm(request.POST, instance=profile)

        # Check validity of both forms
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_view')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Populate forms with existing data
        user_form = UserProfileForm(instance=user)
        if user.usertype == 'student':
            profile_form = StudentProfileForm(instance=profile)
        else: # professor
            profile_form = ProfessorProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_type': user.usertype
    }
    return render(request, 'portal/profile_edit.html', context)

@student_required
def student_application_history_view(request):
    # Optimize by selecting related project details
    applications = Application.objects.filter(studentid=request.user)\
                                    .select_related('projectid')\
                                    .order_by('-applicationdate')
    context = {
        'applications': applications
    }
    return render(request, 'portal/application_history.html', context)

def contact_view(request):
    # Simple static contact page for now.
    # Could be extended with a contact form later (using Django forms).
    if request.method == 'POST':
        # Handle contact form submission if added later
        messages.info(request, "Contact form not yet implemented. Please use the provided email.")
        pass # Replace with form handling logic
    return render(request, 'portal/contact.html')

# Add this view to handle confirm delete template
@professor_required
def delete_project_confirm_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, professorid=request.user)
    application_count = project.applications.count()
    context = {
        'project': project,
        'application_count': application_count
    }
    return render(request, 'portal/confirm_delete.html', context)

from .forms import ApplicationForm
from .models import Application, Project
from django.contrib.auth.decorators import login_required
from .decorators import student_required

@login_required
@student_required
def apply_to_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)  # ✅ request.FILES is necessary for file upload
        if form.is_valid():
            application = form.save(commit=False)
            application.studentid = request.user
            application.projectid = project
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('student_dashboard')
    else:
        form = ApplicationForm()

    return render(request, 'portal/apply_form.html', {
        'form': form,
        'project': project
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Slot
from django.contrib.auth.decorators import login_required

# @login_required
# def calendar_view(request):
#     slots = Slot.objects.all().order_by('date', 'start_time')
#     return render(request, 'portal/calendar.html', {'slots': slots})
# from .models import Slot
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def calendar_view(request):
#     # Show all slots to all users
#     slots = Slot.objects.all().order_by('date', 'start_time')
#     return render(request, 'portal/calendar.html', {'slots': slots})

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json

@login_required
def calendar_view(request):
    slots = Slot.objects.all().order_by('date', 'start_time')

    events = []
    for slot in slots:
        events.append({
            "id": slot.id,
            "title": "Booked" if slot.student else "Free Slot",
            "start": f"{slot.date}T{slot.start_time}",
            "end": f"{slot.date}T{slot.end_time}",
            "color": "#d9534f" if slot.student else "#5cb85c"
        })

    return render(request, 'portal/calendar.html', {
        'slots': slots,
        'event_json': json.dumps(events, cls=DjangoJSONEncoder),
    })




@login_required
def book_slot_view(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    if request.user.usertype == 'student' and slot.student is None:
        slot.student = request.user
        slot.save()
    return redirect('calendar')

from django.contrib import messages
from datetime import datetime
from .models import Slot
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def create_slot_view(request):
    if request.user.usertype != 'professor':
        messages.error(request, "Only professors can create slots.")
        return redirect('calendar')

    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_str = request.POST.get('start_time')
        end_str = request.POST.get('end_time')

        if not (date_str and start_str and end_str):
            messages.error(request, "All fields are required.")
            return redirect('create_slot')

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()

            if start_time >= end_time:
                messages.error(request, "Start time must be before end time.")
                return redirect('create_slot')

            Slot.objects.create(
                professor=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, "Slot created successfully.")
            return redirect('calendar')

        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('create_slot')

    return render(request, 'portal/create_slot.html')
