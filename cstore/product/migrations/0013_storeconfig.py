# Generated by Django 3.2.16 on 2023-12-28 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_remove_companyprofile_phone_numbers'),
        ('product', '0012_auto_20231226_1037'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_discount_type', models.CharField(choices=[('amount', 'Amount'), ('percentage', 'Percentage')], default='percentage', max_length=10)),
                ('default_discount_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('store', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', to='companies.companyprofile')),
            ],
        ),
    ]