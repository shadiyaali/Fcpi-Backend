# Generated by Django 5.0.4 on 2024-05-21 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedback',
            old_name='event',
            new_name='single_event',
        ),
    ]