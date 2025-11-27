

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcheck', '0004_department_alter_teammembership_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='staff', to='healthcheck.department'),
        ),
    ]