# Generated by Django 2.1.5 on 2020-01-09 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('woodcutter', '0015_auto_20181225_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamelog',
            name='version',
            field=models.IntegerField(default=0),
        ),
    ]
