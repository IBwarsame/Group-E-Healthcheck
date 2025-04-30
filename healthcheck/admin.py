# Authors
# Oliver Bryan, Smaran Holkar, Aaron Madhok

from django.contrib import admin
from .models import (
    Team, UserProfile, HealthCheckSession, Vote, TeamMembership, Department
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):

    list_display = ('name', 'department', 'created_at')
    search_fields = ('name', 'department__name')

    list_filter = ('department',)
    readonly_fields = ('created_at',)

    autocomplete_fields = ['department']





@admin.register(HealthCheckSession)
class HealthCheckSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'created_at')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')
    readonly_fields = ('created_at',)
    ordering = ('-start_date',)

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'get_department', 'date_joined')
    list_filter = ('team__department', 'team',)
    search_fields = ('user__username', 'team__name', 'team__department__name')
    autocomplete_fields = ['user', 'team']
    readonly_fields = ('date_joined',)


    @admin.display(description='Department', ordering='team__department__name')
    def get_department(self, obj):
        if obj.team:
            return obj.team.department
        return None
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department')
    list_filter = ('role', 'department')
    search_fields = ('user__username', 'department__name')
    autocomplete_fields = ['user', 'department']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
   list_display = ('user', 'team', 'session', 'card_type', 'vote', 'progress')
   list_filter = ('session', 'team__department', 'team', 'card_type', 'vote', 'progress')
   search_fields = ('user__username', 'team__name', 'session__name', 'comments')
   readonly_fields = ('created_at', 'updated_at')