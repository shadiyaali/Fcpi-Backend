# Generated by Django 5.0.3 on 2024-03-21 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0014_remove_event_speakers'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(blank=True, related_name='events', to='admins.speaker'),
        ),
    ]
