# Generated by Django 5.0.3 on 2024-03-26 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0031_remove_singleevent_event_singleevent_events'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singleevent',
            name='events',
        ),
        migrations.AddField(
            model_name='singleevent',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='single_events', to='admins.event'),
        ),
    ]