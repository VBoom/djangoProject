# Generated by Django 4.1.7 on 2023-03-21 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0006_articlepost_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepost',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
