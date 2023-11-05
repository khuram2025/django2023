from django import forms
from .models import Product, ProductImage, Category, Country, Region, City
from django.utils.translation import gettext_lazy as _

class ProductForm(forms.ModelForm):

    price_unit = forms.ChoiceField(
        choices=[('PKR', 'PKR')],  # Add more currency options as needed
        required=True,
        label=_("Price Unit")
    )
    price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True,
        label=_("Price")
    )
    condition = forms.ChoiceField(
        choices=Product.CONDITION_CHOICES,
        required=True,
        label=_("Condition")
    )
    
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,  # Set to False if geolocation is used
        label=_("Country")
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.none(),  # Initially empty, will be populated via JavaScript or geolocation
        required=False,  # Set to False if geolocation is used
        label=_("Region")
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),  # This should contain all city objects
        required=False,
        label=_("City")
    )
    use_geolocation = forms.BooleanField(
        required=False,
        label=_("Use Geolocation")
    )
    address = forms.CharField(
        required=False,  # Set to False if geolocation is used
        label=_("Address"),
        widget=forms.Textarea
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(parent__isnull=True),
        required=True,
        label="Category"
    )

    subcategory = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Initially empty, will be populated via JavaScript
        required=False,
        label="Subcategory"
    )
    class Meta:
        model = Product
        fields = ['category', 'subcategory', 
                  'price_unit', 'price', 'condition',
                  'country', 'region', 'city', 'use_geolocation', 'address', 
                  'seller_information', 'price_unit', 'price', 'check_with_seller',
                    'item_for_free', 'condition', 'title', 
                    'description', 'seo_title', 'seo_description', 'seo_keywords']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance.category:
                self.fields['subcategory'].queryset = instance.category.get_descendants()
            if instance.country:
                self.fields['region'].queryset = Region.objects.filter(country=instance.country)
            if instance.region:
                self.fields['city'].queryset = City.objects.filter(region=instance.region)

    def save(self, commit=True):
        instance = super().save(commit=False)
        subcategory = self.cleaned_data.get('subcategory')
        city = self.cleaned_data.get('city')
        if subcategory:
            instance.category = subcategory
        if city:
            instance.city = city
            instance.region = city.region
            instance.country = city.region.country
        if commit:
            instance.save()
        return instance


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']

ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=5)
