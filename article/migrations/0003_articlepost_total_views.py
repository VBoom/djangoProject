# Generated by Django 4.1.7 on 2023-03-18 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_alter_articlepost_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepost',
            name='total_views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
