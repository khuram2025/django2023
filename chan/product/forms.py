from django import forms
from .models import Product, SellerInformation, ProductImage, Category, City
from django import forms
from .models import Product, SellerInformation, Category, City

class ProductForm(forms.ModelForm):
    # Add the seller information fields
    contact_name = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=50, required=False)
    phone_visible = forms.BooleanField(required=False)
    email = forms.EmailField(required=False)
    email_visible = forms.BooleanField(required=False)

    class Meta:
        model = Product
        fields = [
            'category', 'city', 'address', 'price', 
            'condition', 'title', 'description',
            # 'seller_information' is not included because we handle it separately
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Add a 'user' kwarg to pass the current user
        super(ProductForm, self).__init__(*args, **kwargs)

        # Here we make sure to only show parent categories (those with no parents)
        self.fields['category'].queryset = Category.objects.filter(parent__isnull=True, status=True)
        self.fields['city'].queryset = City.objects.all()

        # Populate fields if user is authenticated
        if user and user.is_authenticated:
            self.fields['contact_name'].initial = user.full_name
            self.fields['phone_number'].initial = user.mobile
            self.fields['email'].initial = user.email
    def save(self, commit=True):
        product = super(ProductForm, self).save(commit=False)

        # Get or create the SellerInformation for the logged-in user
        if hasattr(self, '_user') and self._user.is_authenticated:
            seller_info, created = SellerInformation.objects.get_or_create(
                user=self._user,
                defaults={
                    'contact_name': self.cleaned_data.get('contact_name', self._user.full_name),
                    'phone_number': self.cleaned_data.get('phone_number', self._user.mobile),
                    'email': self.cleaned_data.get('email', self._user.email),
                    'phone_visible': self.cleaned_data.get('phone_visible'),
                    'email_visible': self.cleaned_data.get('email_visible'),
                }
            )
            if not created:
                # If the SellerInformation instance already exists, update it
                seller_info.contact_name = self.cleaned_data.get('contact_name', self._user.full_name)
                seller_info.phone_number = self.cleaned_data.get('phone_number', self._user.mobile)
                seller_info.email = self.cleaned_data.get('email', self._user.email)
                seller_info.phone_visible = self.cleaned_data.get('phone_visible')
                seller_info.email_visible = self.cleaned_data.get('email_visible')
                seller_info.save()
        else:
            # For guests or when user information is not provided, create new SellerInformation
            seller_info = SellerInformation(
                # ... fields ...
            )
            seller_info.save()

        product.seller_information = seller_info
        if commit:
            product.save()
            self.save_m2m()

        return product

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }



