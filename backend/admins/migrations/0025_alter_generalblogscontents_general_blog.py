# Generated by Django 5.0.4 on 2024-08-21 05:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0024_remove_generalblogscontents_blog_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalblogscontents',
            name='general_blog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blog_contents', to='admins.generalblogs'),
        ),
    ]