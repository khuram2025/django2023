from django import forms
from .models import Product, SellerInformation, ProductImage, Category, City, CustomField
from django import forms
from .models import Product, SellerInformation, Category, City



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
            'category', 'city', 'address', 'price', 'condition', 'title', 'description',
            'youtube_video_url', 'facebook_video_url', 'web_link',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(parent__isnull=True, status=True)
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

            for custom_field in CustomField.objects.filter(categories=product.category):
                field_name = f"custom_field_{custom_field.pk}"
                value = self.cleaned_data.get(field_name)
                if value is not None:
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



