# Generated by Django 5.0.4 on 2024-05-29 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0014_rename_members_boardmember_member_boardmember_board'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ]