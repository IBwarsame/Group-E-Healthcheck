from django.contrib import admin
from .models import Team, UserProfile, HealthCheckSession, Vote

# Register your models here.

admin.site.register(Team)

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
