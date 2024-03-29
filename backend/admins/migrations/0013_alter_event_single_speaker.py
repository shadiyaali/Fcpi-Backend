# Generated by Django 5.0.3 on 2024-03-21 05:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0012_event_single_speaker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='single_speaker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='single_events', to='admins.speaker'),
        ),
    ]
