# Generated by Django 5.0.3 on 2024-03-29 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0034_remove_singleevent_events_singleevent_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='singleevent',
            name='highlights',
            field=models.TextField(blank=True, null=True),
        ),
    ]