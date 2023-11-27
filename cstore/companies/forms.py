from django import forms
from locations.models import City
from .models import CompanyProfile

class CompanyProfileForm(forms.ModelForm):
    line1 = forms.CharField(max_length=255, required=False)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False, empty_label="Select City")

    class Meta:
        model = CompanyProfile
        fields = ['name', 'about', 'logo', 'cover_pic', 'twitter_link', 'facebook_link', 'youtube_link', 'instagram_link', 'line1', 'city']

    def __init__(self, *args, **kwargs):
        super(CompanyProfileForm, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.address:
            self.fields['line1'].initial = self.instance.address.line1
            self.fields['city'].initial = self.instance.address.city
