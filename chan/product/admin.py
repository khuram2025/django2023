from django.contrib import admin
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Specifies the number of extra forms the formset will display.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'condition', 'created_at')
    list_filter = ('category', 'condition')
    search_fields = ('title', 'description')
    inlines = [ProductImageInline]

    # You can add more options for customization as needed.
    # For example, to customize the form fieldsets:
    # fieldsets = (
    #     (None, {
    #         'fields': ('category', 'title', 'description', 'price', 'condition')
    #     }),
    #     ('Location', {
    #         'fields': ('city', 'address')
    #     }),
    #     ('Seller Information', {
    #         'fields': ('seller_information',)
    #     }),
    #     # Add more fieldsets as needed
    # )

# Register your models here.
admin.site.register(Product, ProductAdmin)
