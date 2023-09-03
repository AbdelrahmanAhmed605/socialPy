# Generated by Django 4.2.4 on 2023-09-03 00:46

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_post_media'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.user_profile_picture_upload),
        ),
    ]