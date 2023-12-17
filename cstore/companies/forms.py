from django import forms
from product.models import Category
from locations.models import Address, City
from .models import CompanyProfile, PhoneNumber
from django.utils.translation import gettext_lazy as _

class CompanyProfileForm(forms.ModelForm):
    line1 = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=255, required=False)
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        empty_label="Select City",
        widget=forms.Select(attrs={'class': 'select2'})
    )
    working_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), 
        required=False, 
        widget=forms.CheckboxSelectMultiple,  # Or any other widget you prefer
        label=_("Working Categories")
    )


    class Meta:
        model = CompanyProfile
        fields = ['name', 'about', 'logo', 'cover_pic', 'twitter_link', 'facebook_link',
                   'youtube_link', 'instagram_link', 'line1', 'city', 'working_categories',
                   'phone_number']

    def __init__(self, *args, **kwargs):
        super(CompanyProfileForm, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.address:
            self.fields['line1'].initial = self.instance.address.line1
            self.fields['working_categories'].initial = self.instance.working_categories.all()
            self.fields['city'].initial = self.instance.address.city

            # Schedule initialization would be more complex
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        line1 = self.cleaned_data.get('line1')
        city = self.cleaned_data.get('city')

        # Create or update the address
        if instance.address:
            address = instance.address
            address.line1 = line1
            address.city = city
            address.save()
        else:
            address = Address.objects.create(line1=line1, city=city)
            instance.address = address

        # Save the instance to get an ID, but avoid saving m2m fields
        instance.save()

        # Handle the many-to-many relationship
        if 'working_categories' in self.cleaned_data:
            # Clear any existing categories and add the new ones
            instance.working_categories.set(self.cleaned_data['working_categories'])

        # Save m2m fields if commit is True
        if commit:
            self.save_m2m()

        return instance
