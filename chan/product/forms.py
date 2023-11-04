from django import forms
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'location', 'seller_information', 'price_unit', 'price', 'check_with_seller', 'item_for_free', 'condition', 'title', 'description', 'seo_title', 'seo_description', 'seo_keywords']

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']

ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=5)
