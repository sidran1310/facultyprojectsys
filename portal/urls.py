from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm # Use our custom form
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    # Use custom login form
    path('login/', auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=CustomAuthenticationForm # Specify the custom form
        ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('professor/dashboard/', views.professor_dashboard_view, name='professor_dashboard'),

    path('projects/', views.project_list_view, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:project_id>/apply/', views.apply_project_view, name='apply_project'),

    # Professor specific project management
    path('professor/projects/add/', views.add_project_view, name='add_project'),
    path('professor/projects/edit/<int:project_id>/', views.edit_project_view, name='edit_project'),
    path('professor/projects/delete/<int:project_id>/', views.delete_project_view, name='delete_project'),

    # Professor specific application management
    path('professor/applications/project/<int:project_id>/', views.view_project_applications_view, name='view_project_applications'),
    path('professor/applications/update/<int:application_id>/<str:status>/', views.update_application_status_view, name='update_application_status'), # Status is 'approve' or 'deny'

    # Profile
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # Application History for Student
    path('student/applications/', views.student_application_history_view, name='application_history'),

    # Contact Page
    path('contact/', views.contact_view, name='contact'),

    # Need a confirmation page for delete
    path('professor/projects/delete/<int:project_id>/confirm/', views.delete_project_confirm_view, name='delete_project_confirm'),

    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/create-slot/', views.create_slot_view, name='create_slot'),
    path('calendar/book-slot/<int:slot_id>/', views.book_slot_view, name='book_slot'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)