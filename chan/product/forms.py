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

    # New optional URL fields
    youtube_video_url = forms.URLField(required=False)
    facebook_video_url = forms.URLField(required=False)
    web_link = forms.URLField(required=False)

    class Meta:
        model = Product
        fields = [
            'category', 'city', 'address', 'price', 
            'condition', 'title', 'description',
            # Include the new fields
            'youtube_video_url', 'facebook_video_url', 'web_link',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(parent__isnull=True, status=True)
        self.fields['city'].queryset = City.objects.all()

        if self.user and self.user.is_authenticated:
            # Pre-fill the seller information for authenticated users
            seller_info = getattr(self.user, 'sellerinformation', None)
            self.fields['contact_name'].initial = seller_info.contact_name if seller_info else self.user.full_name
            self.fields['phone_number'].initial = seller_info.phone_number if seller_info else self.user.mobile
            self.fields['email'].initial = seller_info.email if seller_info else self.user.email
            self.fields['phone_visible'].initial = seller_info.phone_visible if seller_info else False
            self.fields['email_visible'].initial = seller_info.email_visible if seller_info else False

    def save(self, commit=True):
        product = super(ProductForm, self).save(commit=False)

        # Handle the seller information
        if self.user and self.user.is_authenticated:
            # Use get_or_create to avoid creating duplicate SellerInformation for the user
            seller_info, created = SellerInformation.objects.get_or_create(
                user=self.user,
                defaults={
                    'contact_name': self.cleaned_data['contact_name'],
                    'phone_number': self.cleaned_data['phone_number'],
                    'email': self.cleaned_data['email'],
                    'phone_visible': self.cleaned_data['phone_visible'],
                    'email_visible': self.cleaned_data['email_visible'],
                }
            )
            product.seller_information = seller_info
        else:
            # For guests, create a new SellerInformation instance
            seller_info = SellerInformation(
                contact_name=self.cleaned_data['contact_name'],
                phone_number=self.cleaned_data['phone_number'],
                email=self.cleaned_data['email'],
                phone_visible=self.cleaned_data['phone_visible'],
                email_visible=self.cleaned_data['email_visible'],
            )
            seller_info.save()
            product.seller_information = seller_info

        product.youtube_video_url = self.cleaned_data.get('youtube_video_url')
        product.facebook_video_url = self.cleaned_data.get('facebook_video_url')
        product.web_link = self.cleaned_data.get('web_link')

        if commit:
            product.save()
            self.save_m2m()  # Save many-to-many data for the form.

        return product

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }



