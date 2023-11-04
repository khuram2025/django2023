from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.template.defaultfilters import slugify

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


class Location(models.Model):
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    region = models.CharField(max_length=100, verbose_name=_("Region"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))

    def __str__(self):
        return f"{self.city}, {self.region}, {self.country}"

class SellerInformation(models.Model):
    contact_name = models.CharField(max_length=255, verbose_name=_("Contact Name"))
    phone_number = models.CharField(max_length=50, verbose_name=_("Phone Number"))
    phone_visible = models.BooleanField(default=False, verbose_name=_("Phone Visible on Ad"))
    email = models.EmailField(verbose_name=_("Email"), blank=True, null=True)
    email_visible = models.BooleanField(default=False, verbose_name=_("Email Visible on Ad"))

    def __str__(self):
        return self.contact_name

class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', _('New')),
        ('used', _('Used')),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name=_("Location"))
    seller_information = models.ForeignKey(SellerInformation, on_delete=models.CASCADE, verbose_name=_("Seller Information"))
    
    # Price and Condition
    price_unit = models.CharField(max_length=10, default='PKR', verbose_name=_("Price Unit"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    check_with_seller = models.BooleanField(default=False, verbose_name=_("Check with Seller"))
    item_for_free = models.BooleanField(default=False, verbose_name=_("Item for Free"))
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, verbose_name=_("Condition"))

    # Listing Information
    title = models.CharField(max_length=255, verbose_name=_("Listing Title"))
    description = models.TextField(verbose_name=_("Listing Description"))
    
    # SEO fields
    seo_title = models.CharField(max_length=255, verbose_name=_("SEO Title"))
    seo_description = models.TextField(verbose_name=_("SEO Description"))
    seo_keywords = models.CharField(max_length=255, verbose_name=_("SEO Keywords"), blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', verbose_name=_("Image"))
    alt_text = models.CharField(max_length=255, verbose_name=_("Alt text"), blank=True, null=True) # Important for SEO and accessibility

    def __str__(self):
        return self.alt_text if self.alt_text else f"Image for {self.product.title}"