# Generated by Django 5.0.3 on 2024-03-21 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0016_alter_event_single_speaker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='ending_time',
        ),
        migrations.RemoveField(
            model_name='event',
            name='event_type',
        ),
        migrations.RemoveField(
            model_name='event',
            name='points',
        ),
        migrations.RemoveField(
            model_name='event',
            name='single_speaker',
        ),
        migrations.RemoveField(
            model_name='event',
            name='starting_time',
        ),
        migrations.RemoveField(
            model_name='event',
            name='topics',
        ),
        migrations.RemoveField(
            model_name='event',
            name='youtube_link',
        ),
    ]