from django.contrib.auth.models import User
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True) # Department names should be unique
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        
class UserProfile(models.Model):
    ROLES = (
        ('engineer', 'Engineer'),
        ('teamLeader', 'Team Leader'),
        ('departmentLeader', 'Department Leader'),
        ('seniorManager', 'Senior Manager'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='engineer')
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL, # If department is deleted, set this field to null
        related_name='staff',      # How to refer to staff from a department object
        null=True,                 # Allow profile to not have a department
        blank=True                 # Allow the field to be blank in forms/admin
    )
    
    def __str__(self):
        dept_name = f" ({self.department.name})" if self.department else ""
        return f"{self.user.username} ({self.get_role_display()}{dept_name})"

class Team(models.Model):
    name = models.CharField(max_length=100)
    # --- Add ForeignKey to Department ---
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='teams',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, through='TeamMembership', related_name='teams_joined')

    def __str__(self):
        return self.name

class HealthCheckSession(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'team')
        ordering = ['team__department__name', 'team__name', 'user__username'] # Order by dept, then team, then user

    def __str__(self):
        return f"{self.user.username} in {self.team.name}"

class Vote(models.Model):
    VOTE_CHOICES = [
        ('good', 'Good'),
        ('neutral', 'Neutral'),
        ('needs_improvement', 'Needs Improvement'),
    ]
    PROGRESS_CHOICES = [
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ]
    CARD_TYPES = [
        ('code_base', 'Code Base Health'),
        ('stakeholder', 'Stakeholder Engagement'),
        ('release', 'Release Process'),
        ('tech_debt', 'Technical Debt'),
        ('teamwork', 'Teamwork & Collaboration'),
        ('delivery', 'Delivery Speed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    session = models.ForeignKey(HealthCheckSession, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    vote = models.CharField(max_length=20, choices=VOTE_CHOICES)
    progress = models.CharField(max_length=20, choices=PROGRESS_CHOICES)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'team', 'session', 'card_type']

    def __str__(self):
        return f"{self.user.username} - {self.team.name} - {self.card_type} - {self.vote}"
    