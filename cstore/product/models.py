from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from companies.models import CompanyProfile

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


from django.db import models
from django.core.validators import RegexValidator

class Customer(models.Model):
    mobile = models.CharField(max_length=15, verbose_name="Mobile Number")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Name")
    store = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='customers', default = 11)
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Opening Balance")

    class Meta:
        unique_together = ['store', 'mobile', 'email']

    def __str__(self):
        return self.mobile


    # Additional methods as needed

class Product(models.Model):
    
    category = models.ForeignKey('product.Category', on_delete=models.CASCADE, related_name='products')
    city = models.ForeignKey('locations.City', on_delete=models.SET_NULL, null=True, verbose_name=_("City"))
    address = models.TextField(verbose_name=_("Address"), blank=True, null=True)
    seller_information = models.ForeignKey(SellerInformation, on_delete=models.CASCADE, related_name='products', verbose_name=_("Seller Information"),blank=True, null=True )
    company = models.ForeignKey('companies.CompanyProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    is_published = models.BooleanField(default=False, verbose_name=_("Published Site-wide"))
    
    # Price and Condition
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    check_with_seller = models.BooleanField(default=False, verbose_name=_("Check with Seller"))
   

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

    def save(self, *args, **kwargs):
        # Open the uploaded image
        pil_image = Image.open(self.image)
        
        if pil_image.mode in ("RGBA", "P"):  # P mode includes palette images
            pil_image = pil_image.convert("RGB")

        # Resize the image
        output_size = (800, 800)  # You can change this to your desired dimensions
        pil_image.thumbnail(output_size, Image.ANTIALIAS)

        # Save the image to a BytesIO object
        output_io_stream = BytesIO()
        pil_image.save(output_io_stream, format='JPEG', quality=85)  # Adjust quality for your needs
        output_io_stream.seek(0)

        # Change the ImageField value to the newly modified image data
        self.image = File(output_io_stream, name=self.image.name)

        super(ProductImage, self).save(*args, **kwargs)

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

class Offer(models.Model):
    class OfferType(models.TextChoices):
        PERCENTAGE = 'PCT', _('Percentage')
        EVENT = 'EVT', _('Event')
        SEASONAL = 'SSN', _('Seasonal')
        CLEARANCE = 'CLR', _('Clearance')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    offer_type = models.CharField(max_length=3, choices=OfferType.choices, verbose_name=_("Offer Type"))
    value = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Value"), help_text=_("Percentage for percentage type, otherwise flat value"))
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"), null=True, blank=True)
    
    def is_active(self):
        # Logic to determine if the offer is currently active
        pass

    def __str__(self):
        return f"{self.product.title} - {self.offer_type}"

class CustomFieldValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_field_values')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.TextField(verbose_name=_("Value"))

    def __str__(self):
        return f"{self.custom_field.name}: {self.value}"

class StoreConfig(models.Model):
    store = models.OneToOneField('companies.CompanyProfile', on_delete=models.CASCADE, related_name='config')
    default_discount_type = models.CharField(max_length=10, choices=[('amount', 'Amount'), ('percentage', 'Percentage')], default='percentage')
    default_discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Define fields for tax configurations and custom charges

    def __str__(self):
        return f"Config for {self.store.name}"

class TaxConfig(models.Model):
    store = models.ForeignKey('companies.CompanyProfile', on_delete=models.CASCADE, related_name='tax_configs')
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage value
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.rate}%"

class CustomCharge(models.Model):
    store = models.ForeignKey('companies.CompanyProfile', on_delete=models.CASCADE, related_name='custom_charges')
    name = models.CharField(max_length=100)
    charge_type = models.CharField(max_length=10, choices=[('amount', 'Amount'), ('percentage', 'Percentage')], default='amount')
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.value}"




class StoreProduct(models.Model):
    store = models.ForeignKey('companies.CompanyProfile', on_delete=models.CASCADE, related_name='store_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_products', null=True, blank=True)  # Nullable for store-exclusive products
    custom_title = models.CharField(max_length=255, verbose_name=_("Custom Title"), blank=True, null=True)
    custom_description = models.TextField(verbose_name=_("Custom Description"), blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Sale Price"), null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Stock Quantity"))
    is_store_exclusive = models.BooleanField(default=False, verbose_name=_("Store Exclusive"))

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Purchase Price"), null=True, blank=True)
    opening_stock = models.PositiveIntegerField(default=0, verbose_name=_("Opening Stock"))
    low_stock_threshold = models.PositiveIntegerField(default=0, verbose_name=_("Low Stock Threshold"))
    current_stock = models.PositiveIntegerField(default=0, verbose_name=_("Current Stock"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # If the store product is being created (not updated), set the current_stock
        if not self.pk:  # pk is None when the object is being created
            self.current_stock = self.opening_stock
        super(StoreProduct, self).save(*args, **kwargs)

    def add_stock(self, quantity, purchase_price=None):
            # Update the stock quantity
            self.stock_quantity += quantity
            self.current_stock += quantity
            if purchase_price:
                self.purchase_price = purchase_price
            self.save()

            # Optionally, record this in a stock entry log
            StoreProductStockEntry.objects.create(
                store_product=self, 
                quantity_added=quantity, 
                purchase_price=purchase_price or self.purchase_price
            )
            
    def __str__(self):
        if self.product:
            return f"{self.store.name} - {self.custom_title or self.product.title}"
        else:
            return f"{self.store.name} - {self.custom_title} (Exclusive)"

    # Function for site admin to publish a store's product changes or exclusive product site-wide
    def publish_to_site(self, admin_user):
        if admin_user.is_admin:  # Check if the user is a site admin
            if self.product:
                # Update and publish existing product
                self.product.title = self.custom_title or self.product.title
                self.product.description = self.custom_description or self.product.description
                self.product.price = self.sale_price or self.product.price
                self.product.is_published = True
                self.product.save()
            else:
                # Create and publish a new product based on the store-exclusive product
                new_product = Product(
                    title=self.custom_title,
                    description=self.custom_description,
                    price=self.custom_price,
                    # Set other necessary fields
                    is_published=True
                )
                new_product.save()
                self.product = new_product  # Link the new product to this store product
                self.is_store_exclusive = False  # No longer exclusive to the store
                self.save()
    def add_stock(self, quantity, purchase_price=None):
        # Update the stock quantity
        self.stock_quantity += quantity
        self.current_stock += quantity
        if purchase_price:
            self.purchase_price = purchase_price
        self.save()

        # Optionally, record this in a stock entry log
        StoreProductStockEntry.objects.create(
            store_product=self, 
            quantity_added=quantity, 
            purchase_price=purchase_price or self.purchase_price
        )

class StoreProductStockEntry(models.Model):
    store_product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name='stock_entries')
    quantity_added = models.PositiveIntegerField(verbose_name=_("Quantity Added"))
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Purchase Price"))
    date_added = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):
        return f"{self.store_product} - Added {self.quantity_added} on {self.date_added} at {self.purchase_price}"

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit', 'Credit'),
        ('partial', 'Partial')
    ]

    store = models.ForeignKey('companies.CompanyProfile', on_delete=models.CASCADE, related_name='store_orders',default=1)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total Price"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    discount_type = models.CharField(max_length=10, choices=[('amount', 'Amount'), ('percentage', 'Percentage')], null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxes = models.ManyToManyField(TaxConfig, blank=True)
    custom_charges = models.ManyToManyField(CustomCharge, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Subtotal"))

    payment_type = models.CharField(max_length=15, choices=PAYMENT_CHOICES, default='cash', verbose_name=_("Payment Type"))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("Paid Amount"))
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("Credit Amount"))

    @property
    def remaining_amount(self):
        """Calculate the remaining amount that is due."""
        return max(self.total_price - self.paid_amount, 0)

    # Method to calculate total tax
    def calculate_tax(self):
        total_tax = sum([tax.rate for tax in self.taxes.all()])
        return (self.subtotal * total_tax) / 100


    def __str__(self):
        return f"Order {self.id} from {self.store.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))

    discount_type = models.CharField(max_length=10, choices=[('amount', 'Amount'), ('percentage', 'Percentage')], null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.product.title} in Order {self.order.id}"

    @property
    def total_price(self):
        return self.quantity * self.price
    
