from django import forms
from .models import Category, Product, ProductImage

class ProductForm(forms.ModelForm):
    
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        subcategory = self.cleaned_data.get('subcategory')
        if subcategory:
            instance.category = subcategory
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'location', 'seller_information', 'price_unit', 'price', 'check_with_seller', 'item_for_free', 'condition', 'title', 'description', 'seo_title', 'seo_description', 'seo_keywords']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance.category:
                self.fields['subcategory'].queryset = instance.category.get_descendants()
                
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']

ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=5)
