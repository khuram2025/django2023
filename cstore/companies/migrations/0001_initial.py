# Generated by Django 3.2.16 on 2023-11-29 10:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], max_length=3)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='companies.branch')),
            ],
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phone_numbers_rel', to='companies.branch')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('verified', models.BooleanField(default=False)),
                ('about', models.TextField()),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('cover_pic', models.ImageField(blank=True, null=True, upload_to='company_covers/')),
                ('twitter_link', models.URLField(blank=True, null=True)),
                ('facebook_link', models.URLField(blank=True, null=True)),
                ('youtube_link', models.URLField(blank=True, null=True)),
                ('instagram_link', models.URLField(blank=True, null=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companies', to='locations.address')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_companies', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
