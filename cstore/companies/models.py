from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from product.models import Category  # Import your existing Category model

class CompanyProfile(models.Model):
    name = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)
    about = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cover_pic = models.ImageField(upload_to='company_covers/', blank=True, null=True)

    twitter_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Branch(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=200)
    working_categories = models.ManyToManyField(Category)
    phone_numbers = models.ManyToManyField('PhoneNumber', related_name='branch_phone_numbers')
    opening_hours = models.TextField(help_text="Describe opening hours")

    def __str__(self):
        return f"{self.name} ({self.company.name})"


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

