from django import forms

from companies.models import CompanyProfile
from .models import CustomFieldValue, Order, Product, SellerInformation, ProductImage, Category, City, CustomField, StoreProductStockEntry
from django import forms
from .models import Product, SellerInformation, Category, City ,StoreProduct



class ProductForm(forms.ModelForm):
    contact_name = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=50, required=False)
    phone_visible = forms.BooleanField(required=False)
    email = forms.EmailField(required=False)
    email_visible = forms.BooleanField(required=False)
    youtube_video_url = forms.URLField(required=False)
    facebook_video_url = forms.URLField(required=False)
    web_link = forms.URLField(required=False)

    class Meta:
        model = Product
        fields = [
            'category', 'city', 'address', 'price','title', 'description',
            'youtube_video_url', 'facebook_video_url', 'web_link',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        company_profiles = kwargs.pop('company_profiles', None)
        super(CompanyProductForm, self).__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(parent__isnull=True, status=True)
        self.fields['city'].queryset = City.objects.all()

        if company_profiles and company_profiles.first().address:
                self.fields.pop('address', None)
                self.fields.pop('city', None)
        else:
            self.fields['address'].required = False
            self.fields['city'].required = False
            self.fields['city'].queryset = City.objects.all()

        if self.user and self.user.is_authenticated:
            seller_info = getattr(self.user, 'sellerinformation', None)
            self.fields['contact_name'].initial = seller_info.contact_name if seller_info else self.user.full_name
            self.fields['phone_number'].initial = seller_info.phone_number if seller_info else self.user.mobile
            self.fields['email'].initial = seller_info.email if seller_info else self.user.email
            self.fields['phone_visible'].initial = seller_info.phone_visible if seller_info else False
            self.fields['email_visible'].initial = seller_info.email_visible if seller_info else False

        if self.instance.pk and self.instance.category:
            category = self.instance.category
        else:
            category = None

        custom_fields_qs = CustomField.objects.filter(categories=category)
        for custom_field in custom_fields_qs:
            field_name = f"custom_field_{custom_field.pk}"
            self.fields[field_name] = self.get_field_for_type(custom_field.field_type)
            if self.instance.pk:
                try:
                    value = CustomFieldValue.objects.get(product=self.instance, custom_field=custom_field).value
                    self.initial[field_name] = value
                except CustomFieldValue.DoesNotExist:
                    self.initial[field_name] = None

    def get_field_for_type(self, field_type):
        field_class = forms.CharField
        field_kwargs = {'required': False}

        if field_type == 'number':
            field_class = forms.DecimalField
        elif field_type == 'email':
            field_class = forms.EmailField
        elif field_type == 'phone':
            field_class = forms.CharField
        elif field_type == 'url':
            field_class = forms.URLField
        elif field_type == 'color':
            field_class = forms.CharField
        elif field_type == 'textarea':
            field_class = forms.CharField
            field_kwargs['widget'] = forms.Textarea
        elif field_type == 'select':
            field_class = forms.ChoiceField
            field_kwargs['choices'] = []
        elif field_type == 'checkbox':
            field_class = forms.MultipleChoiceField
            field_kwargs['widget'] = forms.CheckboxSelectMultiple
            field_kwargs['choices'] = []
        elif field_type == 'radio':
            field_class = forms.ChoiceField
            field_kwargs['widget'] = forms.RadioSelect
            field_kwargs['choices'] = []
        elif field_type == 'date':
            field_class = forms.DateField
        elif field_type == 'date_interval':
            field_class = forms.CharField

        return field_class(**field_kwargs)

    def save(self, commit=True):
        product = super(ProductForm, self).save(commit=False)

        if self.user and self.user.is_authenticated:
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

            # After saving the product, now save custom fields
            for field_name, value in self.cleaned_data.items():
                if field_name.startswith('custom_field_'):
                    field_id = int(field_name.split('_')[-1])
                    custom_field = CustomField.objects.get(id=field_id)
                    CustomFieldValue.objects.update_or_create(
                        product=product,
                        custom_field=custom_field,
                        defaults={'value': value}
                    )

            self.save_m2m()

        return product






class CompanyProductForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=50, required=False)
    company = forms.ModelChoiceField(queryset=CompanyProfile.objects.all(), empty_label="Select Company", required=False)


    class Meta:
        model = Product
        exclude = ['seller_information','view_count']  # Exclude the seller_information field

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        company_profiles = kwargs.pop('company_profiles', None)
        super(CompanyProductForm, self).__init__(*args, **kwargs)

        # Set querysets for category, city, and company fields
        self.fields['category'].queryset = Category.objects.filter(parent__isnull=True, status=True)
        self.fields['city'].queryset = City.objects.all()

        if self.user and self.user.is_authenticated:
            if company_profiles:
                self.fields['company'].queryset = company_profiles
            else:
                self.fields['company'].queryset = CompanyProfile.objects.filter(owner=self.user)

            company_profile = CompanyProfile.objects.filter(owner=self.user).first()
            if company_profile:
                self.fields['address'].initial = company_profile.address
                self.fields['phone_number'].initial = company_profile.phone_number

    def get_field_for_type(self, field_type):
        field_class = forms.CharField
        field_kwargs = {'required': False}

        if field_type == 'number':
            field_class = forms.DecimalField
        elif field_type == 'email':
            field_class = forms.EmailField
        elif field_type == 'phone':
            field_class = forms.CharField
        elif field_type == 'url':
            field_class = forms.URLField
        elif field_type == 'color':
            field_class = forms.CharField
        elif field_type == 'textarea':
            field_class = forms.CharField
            field_kwargs['widget'] = forms.Textarea
        elif field_type == 'select':
            field_class = forms.ChoiceField
            field_kwargs['choices'] = []
        elif field_type == 'checkbox':
            field_class = forms.MultipleChoiceField
            field_kwargs['widget'] = forms.CheckboxSelectMultiple
            field_kwargs['choices'] = []
        elif field_type == 'radio':
            field_class = forms.ChoiceField
            field_kwargs['widget'] = forms.RadioSelect
            field_kwargs['choices'] = []
        elif field_type == 'date':
            field_class = forms.DateField
        elif field_type == 'date_interval':
            field_class = forms.CharField

        return field_class(**field_kwargs)

    def save(self, commit=True):
        product = super(CompanyProductForm, self).save(commit=False)
        
        # Use the selected company from the form
        if self.cleaned_data.get('company'):
            product.company_information = self.cleaned_data['company']
        else:
            # Handle the case where no company is selected
            # You might want to raise a validation error or handle this scenario as per your business logic
            pass

        product.youtube_video_url = self.cleaned_data.get('youtube_video_url')
        product.facebook_video_url = self.cleaned_data.get('facebook_video_url')
        product.web_link = self.cleaned_data.get('web_link')

        if commit:
            product.save()
            # After saving the product, now save custom fields
            for field_name, value in self.cleaned_data.items():
                if field_name.startswith('custom_field_'):
                    field_id = int(field_name.split('_')[-1])
                    custom_field = CustomField.objects.get(id=field_id)
                    CustomFieldValue.objects.update_or_create(
                        product=product,
                        custom_field=custom_field,
                        defaults={'value': value}
                    )

            self.save_m2m()
        return product

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }




class StoreProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)
    product_images = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))


    class Meta:
        model = StoreProduct
        fields = ['custom_title', 'custom_description', 'sale_price', 'stock_quantity', 'category', 'city', 'purchase_price', 'opening_stock', 'low_stock_threshold','product_images']

class AddStockForm(forms.Form):
    vendor = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.none(),  # Initially empty queryset
        required=False,
        label="Vendor",
        help_text="Select the vendor company"
    )
    
    additional_quantity = forms.IntegerField(
        min_value=1, 
        required=True,
        label="Additional Quantity",
        help_text="Enter the quantity of stock to be added"
    )

    purchase_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        label="Purchase Price",
        help_text="Enter the purchase price per unit (optional)"
    )

    def __init__(self, *args, **kwargs):
        store_owner = kwargs.pop('store_owner', None)
        super(AddStockForm, self).__init__(*args, **kwargs)
        if store_owner:
            # Exclude the current company from the list of vendors
            self.fields['vendor'].queryset = CompanyProfile.objects.exclude(owner=store_owner)

    def clean_additional_quantity(self):
        quantity = self.cleaned_data['additional_quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity


from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'store',  # Use a ForeignKey widget to select the store
            'customer',  # Use a ForeignKey widget to select the customer
            'total_price',
            'discount_type',
            'discount_value',
            'taxes',  # Use a ModelMultipleChoiceField to select taxes
            'custom_charges',  # Use a ModelMultipleChoiceField to select custom charges
            'subtotal',
            'payment_type',
            'paid_amount',
            'credit_amount',
        ]



class EditStockEntryForm(forms.ModelForm):
    class Meta:
        model = StoreProductStockEntry
        fields = ['quantity_added', 'purchase_price']
        labels = {
            'quantity_added': 'Quantity Added',
            'purchase_price': 'Purchase Price',
        }
        help_texts = {
            'quantity_added': 'Enter the updated quantity of stock added',
            'purchase_price': 'Enter the updated purchase price per unit',
        }

    def clean_quantity_added(self):
        quantity = self.cleaned_data['quantity_added']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity