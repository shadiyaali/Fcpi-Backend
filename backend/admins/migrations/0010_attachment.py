# Generated by Django 5.0.4 on 2024-07-25 04:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0009_speaker_facebook_speaker_instagram_speaker_linkedin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='attachments/')),
                ('single_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='admins.singleevent')),
            ],
        ),
    ]