import random
from django.contrib.auth.models import User
from healthcheck.models import Team, HealthCheckSession, Vote

CARD_TYPES = [
    ('code_quality', 'Code Quality'),
    ('requirements_clarity', 'Requirements Clarity'),
    ('testing_coverage', 'Testing Coverage'),
    ('deployment_process', 'Deployment Process'),
    ('tooling_infrastructure', 'Tooling & Infrastructure'),
    ('team_collaboration', 'Team Collaboration'),
    ('delivery_predictability', 'Delivery Predictability'),
    ('stakeholder_communication', 'Stakeholder Communication'),
    ('knowledge_sharing', 'Knowledge Sharing'),
    ('workload_balance', 'Workload Balance'),
]

VOTE_CHOICES = ['good', 'neutral', 'needs_improvement']
PROGRESS_CHOICES = ['improving', 'stable', 'declining']

users = list(User.objects.all())
teams = list(Team.objects.all())
sessions = list(HealthCheckSession.objects.all())

if not users or not teams or not sessions:
    print("Please ensure you have users, teams, and sessions in your database.")
else:
    for user in users:
        for team in teams:
            for session in sessions:
                for card_type, _ in CARD_TYPES:
                    if random.random() < 0.5:
                        vote_value = random.choice(VOTE_CHOICES)
                        progress_value = random.choice(PROGRESS_CHOICES)
                        comments = f"Auto-generated comment for {card_type} by {user.username}"
                        Vote.objects.update_or_create(
                            user=user,
                            team=team,
                            session=session,
                            card_type=card_type,
                            defaults={
                                'vote': vote_value,
                                'progress': progress_value,
                                'comments': comments,
                            }
                        )
    print("Random votes generated!")
