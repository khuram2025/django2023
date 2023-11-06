from django import forms
from .models import Product, SellerInformation, ProductImage, Category, City

class ProductForm(forms.ModelForm):
    # Add the seller information fields
    contact_name = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=50)
    phone_visible = forms.BooleanField(required=False)
    email = forms.EmailField(required=False)
    email_visible = forms.BooleanField(required=False)

    class Meta:
        model = Product
        fields = [
            'category', 'city', 'address', 'price', 
            'condition', 'title', 'description'
            # 'seller_information' is not included because we handle it separately
        ]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Here we make sure to only show parent categories (those with no parents)
        self.fields['category'].queryset = Category.objects.filter(parent__isnull=True, status=True)
        self.fields['city'].queryset = City.objects.all()

        # If the form is being used to update an existing instance,
        # populate the seller information fields:
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance.seller_information:
                self.fields['contact_name'].initial = instance.seller_information.contact_name
                self.fields['phone_number'].initial = instance.seller_information.phone_number
                self.fields['phone_visible'].initial = instance.seller_information.phone_visible
                self.fields['email'].initial = instance.seller_information.email
                self.fields['email_visible'].initial = instance.seller_information.email_visible

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        # Handle the seller information
        seller_info, created = SellerInformation.objects.update_or_create(
            contact_name=self.cleaned_data.get('contact_name'),
            defaults={
                'phone_number': self.cleaned_data.get('phone_number'),
                'phone_visible': self.cleaned_data.get('phone_visible'),
                'email': self.cleaned_data.get('email'),
                'email_visible': self.cleaned_data.get('email_visible'),
            }
        )
        instance.seller_information = seller_info
       

        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many data for the form.

        return instance

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }



