# Generated by Django 5.0.4 on 2024-05-28 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0011_boardmember'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boardmember',
            old_name='member',
            new_name='members',
        ),
    ]