from django.db import models
from account.models import CustomUser
from phonenumber_field.modelfields import PhoneNumberField
from product.models import Category  # Import your existing Category model
from django.db.models.signals import post_save
from django.dispatch import receiver


class CompanyProfile(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE, related_name='owned_companies')


    verified = models.BooleanField(default=False)
    about = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cover_pic = models.ImageField(upload_to='company_covers/', blank=True, null=True)

    twitter_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the instance is new
        super().save(*args, **kwargs)
        if is_new:
            # Create a default branch for new company
            Branch.objects.create(company=self, name=f"Main Branch of {self.name}")

    def __str__(self):
        return self.name

class Branch(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=200)
    working_categories = models.ManyToManyField(Category)
    phone_numbers = models.ManyToManyField('PhoneNumber', related_name='branch_phone_numbers')
   
    

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
    
class Location(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}, {self.country} ({self.branch.name})"

class PhoneNumber(models.Model):
    branch = models.ForeignKey(Branch, related_name='phone_numbers_rel', on_delete=models.CASCADE)
    number = PhoneNumberField()
    
    def __str__(self):
        return str(self.number)

