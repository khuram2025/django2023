# Generated by Django 3.2.16 on 2023-12-06 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_branch_phone_numbers'),
        ('product', '0002_auto_20231130_0721'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name='Published Site-wide'),
        ),
        migrations.CreateModel(
            name='StoreProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Custom Title')),
                ('custom_description', models.TextField(blank=True, null=True, verbose_name='Custom Description')),
                ('custom_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Custom Price')),
                ('stock_quantity', models.PositiveIntegerField(default=0, verbose_name='Stock Quantity')),
                ('is_store_exclusive', models.BooleanField(default=False, verbose_name='Store Exclusive')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='store_products', to='product.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='store_products', to='companies.companyprofile')),
            ],
        ),
    ]