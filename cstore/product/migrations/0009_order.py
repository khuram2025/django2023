# Generated by Django 3.2.16 on 2023-12-22 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_remove_companyprofile_phone_numbers'),
        ('product', '0008_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Total Price')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_orders', to='product.customer')),
                ('store', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='store_orders', to='companies.companyprofile')),
            ],
        ),
    ]
