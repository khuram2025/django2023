# Generated by Django 3.2.16 on 2023-11-30 04:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='seo_description',
        ),
        migrations.RemoveField(
            model_name='category',
            name='seo_keywords',
        ),
        migrations.RemoveField(
            model_name='category',
            name='seo_title',
        ),
    ]
