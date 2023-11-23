from django import forms
from .models import CompanyProfile

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['name', 'about', 'logo', 'cover_pic', 'twitter_link', 'facebook_link', 'youtube_link', 'instagram_link']
