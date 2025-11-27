

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcheck', '0003_teammembership_team_members'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='teammembership',
            options={'ordering': ['team__department__name', 'team__name', 'user__username']},
        ),
        migrations.AddField(
            model_name='team',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='teams', to='healthcheck.department'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='healthcheck.department'),
        ),
    ]