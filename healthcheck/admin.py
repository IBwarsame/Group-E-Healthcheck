from django.contrib import admin
from .models import (
    Team, UserProfile, HealthCheckSession, Vote, TeamMembership, Department # Added Department
)

# --- Register Department ---
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)

# --- Update Team Admin ---
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    # Add 'department' to list_display
    list_display = ('name', 'department', 'created_at')
    search_fields = ('name', 'department__name') # Allow searching by department name too
    # Add 'department' to list_filter
    list_filter = ('department',)
    readonly_fields = ('created_at',)
    # Make department selectable with autocomplete (good for many departments)
    autocomplete_fields = ['department']
    # Or use raw_id_fields for a simpler popup selector
    # raw_id_fields = ['department']


# --- Existing Registrations ---
@admin.register(HealthCheckSession)
class HealthCheckSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'created_at')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')
    readonly_fields = ('created_at',)
    ordering = ('-start_date',)

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'get_department', 'date_joined') # Added department display
    list_filter = ('team__department', 'team',) # Filter by department, then team
    search_fields = ('user__username', 'team__name', 'team__department__name') # Added department search
    autocomplete_fields = ['user', 'team']
    readonly_fields = ('date_joined',)

    # Helper method to display department in TeamMembership list
    @admin.display(description='Department', ordering='team__department__name')
    def get_department(self, obj):
        if obj.team:
            return obj.team.department
        return None
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department') # Add department
    list_filter = ('role', 'department')          # Add department
    search_fields = ('user__username', 'department__name') # Add department
    autocomplete_fields = ['user', 'department'] # Add department

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
   list_display = ('user', 'team', 'session', 'card_type', 'vote', 'progress')
   list_filter = ('session', 'team__department', 'team', 'card_type', 'vote', 'progress')
   search_fields = ('user__username', 'team__name', 'session__name', 'comments')
   readonly_fields = ('created_at', 'updated_at')
