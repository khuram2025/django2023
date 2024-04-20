from django.db import models
from account.models import CustomUser
from locations.models import Address
from phonenumber_field.modelfields import PhoneNumberField

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.apps import apps





class CompanyProfile(models.Model):
    name = models.CharField(max_length=200)
    
    owner = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE, related_name='owned_companies')
    verified = models.BooleanField(default=False)
    working_categories = models.ManyToManyField(
        'product.Category',
        blank=True, 
        null=True,
        related_name='companies', 
        verbose_name=_("Working Categories")
    )
    about = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    

    cover_pic = models.ImageField(upload_to='company_covers/', blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='companies')

    def import_category(self):
        Category = apps.get_model('product', 'Category')

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the instance is new
        super().save(*args, **kwargs)
        if is_new:
            # Create a default branch for new company
            Branch.objects.create(company=self, name=f"Main Branch of {self.name}")


    def __str__(self):
        return self.name

class Branch(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='branches', null=True)
    name = models.CharField(max_length=200)
    working_categories = models.ManyToManyField('product.Category')
    phone_numbers = models.ManyToManyField('PhoneNumber', related_name='branch_phone_numbers')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='branches')

   
    def __str__(self):
        return f"{self.name} ({self.company.name})"

class Schedule(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_display()} ({self.start_time} - {self.end_time})"

class PhoneNumber(models.Model):
    branch = models.ForeignKey(Branch, related_name='phone_numbers_rel', on_delete=models.CASCADE)
    number = PhoneNumberField()
    
    def __str__(self):
        return str(self.number)

