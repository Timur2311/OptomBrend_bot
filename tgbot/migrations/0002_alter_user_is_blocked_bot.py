# Generated by Django 3.2.12 on 2022-03-21 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_blocked_bot',
            field=models.BooleanField(default=True),
        ),
    ]
