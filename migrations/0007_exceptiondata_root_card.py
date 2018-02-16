# Generated by Django 2.0 on 2018-02-13 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('woodcutter', '0006_auto_20180213_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='exceptiondata',
            name='root_card',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='woodcutter.CardData', verbose_name='root Card'),
            preserve_default=False,
        ),
    ]