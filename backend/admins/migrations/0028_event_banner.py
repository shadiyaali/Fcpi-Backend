# Generated by Django 5.0.3 on 2024-03-25 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0027_remove_singleevent_days_event_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to='events/'),
        ),
    ]
