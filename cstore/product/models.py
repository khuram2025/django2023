from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser
from locations.models import City
from mptt.models import MPTTModel, TreeForeignKey
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.postgres.fields import JSONField as PostgresJSONField
from django.db.models import JSONField as DefaultJSONField

class Category(MPTTModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("Slug"))
    description = models.TextField(verbose_name=_("Description"))
    seo_title = models.CharField(max_length=70, blank=True, verbose_name=_("SEO Title"))
    seo_description = models.CharField(max_length=160, blank=True, verbose_name=_("SEO Description"))
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name=_("SEO Keywords"))
    status = models.BooleanField(default=True, verbose_name=_("Status (Active/Disabled)"))
    icon = models.ImageField(upload_to='icons/', verbose_name=_("Icon"), blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', verbose_name=_("Category Image"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        unique_together = ('parent', 'slug',)  # Changed to slug

    def __str__(self):
        return self.title

    def is_subcategory(self):
        return self.parent is not None

    def is_root_category(self):
        return self.parent is None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class SellerInformation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, verbose_name=_("User Account"))
    contact_name = models.CharField(max_length=255, verbose_name=_("Contact Name"))
    phone_number = models.CharField(max_length=50, verbose_name=_("Phone Number"))
    phone_visible = models.BooleanField(default=False, verbose_name=_("Phone Visible on Ad"))
    email = models.EmailField(verbose_name=_("Email"), blank=True, null=True)
    email_visible = models.BooleanField(default=False, verbose_name=_("Email Visible on Ad"))

    last_login = models.DateTimeField(verbose_name=_("Last Login"), default=timezone.now)
    member_since = models.DateTimeField(verbose_name=_("Member Since"), auto_now_add=True)
    status = models.BooleanField(default=False, verbose_name=_("Status (Online/Offline)"))

    def __str__(self):
        return self.contact_name
    
    
    @property
    def number_of_listings(self):
        # This will return the count of products related to this SellerInformation instance
        if self.user:
            return Product.objects.filter(seller_information=self).count()
        return 0


class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', _('New')),
        ('used', _('Used')),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name=_("City"))
    address = models.TextField(verbose_name=_("Address"), blank=True, null=True)
    seller_information = models.ForeignKey(SellerInformation, on_delete=models.CASCADE, related_name='products', verbose_name=_("Seller Information"))
    
    # Price and Condition
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    check_with_seller = models.BooleanField(default=False, verbose_name=_("Check with Seller"))
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, verbose_name=_("Condition"))

    # Listing Information
    title = models.CharField(max_length=255, verbose_name=_("Listing Title"))
    description = models.TextField(verbose_name=_("Listing Description"))
    
    # Optional link fields
    youtube_video_url = models.URLField(verbose_name=_("YouTube Video URL"), blank=True, null=True)
    facebook_video_url = models.URLField(verbose_name=_("Facebook Video URL"), blank=True, null=True)
    web_link = models.URLField(verbose_name=_("Web Link"), blank=True, null=True)

    custom_fields = DefaultJSONField(blank=True, null=True)
   
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', verbose_name=_("Image"))
    alt_text = models.CharField(max_length=255, verbose_name=_("Alt text"), blank=True, null=True) # Important for SEO and accessibility

    def __str__(self):
        return self.alt_text if self.alt_text else f"Image for {self.product.title}"
    
class CustomField(models.Model):
    FIELD_TYPES = [
        ('number', _('Number')),
        ('email', _('Email')),
        ('phone', _('Phone')),
        ('url', _('URL')),
        ('color', _('Color')),
        ('textarea', _('Textarea')),
        ('select', _('Select Box')),
        ('checkbox', _('Checkbox')),
        ('radio', _('Radio Button')),
        ('date', _('Date')),
        ('date_interval', _('Date Interval')),
    ]
    
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES, verbose_name=_("Type"))
    
    # For select, checkbox, and radio fields, store options as comma-separated values
    options = models.TextField(verbose_name=_("Options"), blank=True, help_text=_("Comma-separated values"))

    is_searchable = models.BooleanField(default=False, verbose_name=_("Available for Search"))

    categories = models.ManyToManyField(
        Category,
        related_name='custom_fields',
        verbose_name=_('Categories'),
        blank=True,
    )
    
    def __str__(self):
        return self.name

class CategoryCustomField(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='category_custom_fields',  # Unique related_name
        on_delete=models.CASCADE
    )
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category.title} - {self.custom_field.name}"


class CustomFieldValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_field_values')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.TextField(verbose_name=_("Value"))

    def __str__(self):
        return f"{self.custom_field.name}: {self.value}"
