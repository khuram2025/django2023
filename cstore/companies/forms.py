from django import forms
from product.models import Category
from locations.models import City
from .models import CompanyProfile
from django.utils.translation import gettext_lazy as _

class CompanyProfileForm(forms.ModelForm):
    line1 = forms.CharField(max_length=255, required=False)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False, empty_label="Select City")
    working_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), 
        required=False, 
        widget=forms.CheckboxSelectMultiple,  # Or any other widget you prefer
        label=_("Working Categories")
    )


    class Meta:
        model = CompanyProfile
        fields = ['name', 'about', 'logo', 'cover_pic', 'twitter_link', 'facebook_link', 'youtube_link', 'instagram_link', 'line1', 'city', 'working_categories']

    def __init__(self, *args, **kwargs):
        super(CompanyProfileForm, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.address:
            self.fields['line1'].initial = self.instance.address.line1
            self.fields['working_categories'].initial = self.instance.working_categories.all()
            self.fields['city'].initial = self.instance.address.city
        

