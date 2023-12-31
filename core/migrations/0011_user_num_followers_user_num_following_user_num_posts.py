# Generated by Django 4.2.4 on 2023-08-19 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_post_comment_count_post_like_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='num_followers',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='num_following',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='num_posts',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
