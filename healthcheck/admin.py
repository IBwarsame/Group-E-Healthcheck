from django.contrib import admin
from .models import (
    Team, UserProfile, HealthCheckSession, Vote, TeamMembership
)

# Register your models here.

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    

@admin.register(HealthCheckSession)
class HealthCheckSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'created_at')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')
    readonly_fields = ('created_at',)
    ordering = ('-start_date',)

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'date_joined')
    list_filter = ('team',)
    search_fields = ('user__username', 'team__name')
    autocomplete_fields = ['user', 'team']
    readonly_fields = ('date_joined',)