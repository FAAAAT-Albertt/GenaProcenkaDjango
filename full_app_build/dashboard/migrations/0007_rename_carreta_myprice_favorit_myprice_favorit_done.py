# Generated by Django 5.0.6 on 2024-07-11 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_myprice_amry_done_myprice_armtek_done_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myprice',
            old_name='carreta',
            new_name='favorit',
        ),
        migrations.AddField(
            model_name='myprice',
            name='favorit_done',
            field=models.BooleanField(default=False),
        ),
    ]