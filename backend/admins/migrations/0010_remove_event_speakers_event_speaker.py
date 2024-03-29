# Generated by Django 5.0.3 on 2024-03-21 04:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0009_rename_topic_event_event_name_event_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='speakers',
        ),
        migrations.AddField(
            model_name='event',
            name='speaker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='admins.speaker'),
        ),
    ]
