# serializers.py

from rest_framework import serializers
from .models import CompanyProfile

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['name', 'about', 'logo', 'cover_pic', 'twitter_link', 'facebook_link',
                  'youtube_link', 'instagram_link', 'phone_number', 'address']
        read_only_fields = ['owner']
