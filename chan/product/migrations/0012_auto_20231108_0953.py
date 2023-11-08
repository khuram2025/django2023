# Generated by Django 3.2.16 on 2023-11-08 06:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_alter_sellerinformation_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='facebook_video_url',
            field=models.URLField(blank=True, null=True, verbose_name='Facebook Video URL'),
        ),
        migrations.AddField(
            model_name='product',
            name='web_link',
            field=models.URLField(blank=True, null=True, verbose_name='Web Link'),
        ),
        migrations.AddField(
            model_name='product',
            name='youtube_video_url',
            field=models.URLField(blank=True, null=True, verbose_name='YouTube Video URL'),
        ),
        migrations.AlterField(
            model_name='product',
            name='seller_information',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.sellerinformation', verbose_name='Seller Information'),
        ),
    ]
