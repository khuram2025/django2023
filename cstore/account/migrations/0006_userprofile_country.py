# Generated by Django 3.2.16 on 2023-11-23 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20231122_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
