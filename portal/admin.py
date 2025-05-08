from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Project, Application


# Customize User admin display
class UserAdmin(BaseUserAdmin):
    # Which fields to display in the User list view
    list_display = ('email', 'name', 'usertype', 'is_staff', 'is_active', 'date_joined')
    # Which fields to allow filtering by
    list_filter = ('usertype', 'is_staff', 'is_active')
    # Which fields to search
    search_fields = ('email', 'name')
    # How to order users
    ordering = ('email',)
    # Fields to display on the User editing form
    fieldsets = (
        (None, {'fields': ('email', 'password')}), # Password field handled by Django
        ('Personal info', {'fields': ('name', 'usertype')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fields needed when creating a user via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'usertype', 'password', 'password2'), # Add usertype here
        }),
    )
    # Make usertype visible but not editable after creation? Or allow editing.
    readonly_fields = ('last_login', 'date_joined')

# portal/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Project, Application # Import custom User

# Inline admin for Profile on User page
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    # Control which fields show based on usertype (can be complex in inline)
    # Or just show all and let admin know which apply
    fields = ('academicdetails', 'facultyinformation', 'branch')

# Customize User admin display using decorator
@admin.register(User) # Use decorator for cleaner registration
class UserAdmin(BaseUserAdmin):
    # Add the inline directly to the class definition
    inlines = (ProfileInline,)
    # Which fields to display in the User list view
    list_display = ('email', 'name', 'usertype', 'is_staff', 'is_active', 'date_joined')
    # Which fields to allow filtering by
    list_filter = ('usertype', 'is_staff', 'is_active')
    # Which fields to search
    search_fields = ('email', 'name')
    # How to order users
    ordering = ('email',)
    # Fields to display on the User editing form
    # Make sure 'usertype' is included here if you want to see/edit it
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'usertype')}), # Added usertype
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fields needed when creating a user via admin
    # Make sure 'usertype' is included here
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('usertype',)}), # Added usertype
    )
    readonly_fields = ('last_login', 'date_joined')

# Customize Project admin display
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'professorname', 'status', 'category', 'branch', 'created_at')
    list_filter = ('status', 'category', 'branch', 'professorid__name') # Filter by professor name directly
    search_fields = ('title', 'description', 'professorname')
    autocomplete_fields = ['professorid'] # Better UI
    readonly_fields = ('professorname', 'created_at', 'updated_at')

# Customize Application admin display
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'student_name', 'status', 'applicationdate')
    list_filter = ('status', 'projectid__title', 'studentid__name') # Filter by related fields
    search_fields = ('projectid__title', 'studentid__name', 'studentid__email', 'statementofinterest')
    autocomplete_fields = ['projectid', 'studentid']
    readonly_fields = ('applicationdate',)

    # Method to display project title in list_display
    def project_title(self, obj):
        # Add check in case projectid is somehow None (though unlikely with FK)
        return obj.projectid.title if obj.projectid else 'N/A'
    project_title.short_description = 'Project Title'
    project_title.admin_order_field = 'projectid__title'

    # Method to display student name in list_display
    def student_name(self, obj):
        return obj.studentid.name if obj.studentid else 'N/A'
    student_name.short_description = 'Student Name'
    student_name.admin_order_field = 'studentid__name' # Allow sorting


# No need to register Profile separately if it's inline
# admin.site.register(Profile)