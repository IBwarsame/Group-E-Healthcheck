from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    ROLES = (
        ('engineer', 'Engineer'),
        ('teamLeader', 'Team Leader'),
        ('departmentLeader', 'Department Leader'),
        ('seniorManager', 'Senior Manager'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='engineer')
