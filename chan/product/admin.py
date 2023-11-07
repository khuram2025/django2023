from django.contrib import admin
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Specifies the number of extra forms the formset will display.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'condition', 'created_at', 'owner_status')
    list_filter = ('category', 'condition')
    search_fields = ('title', 'description')
    inlines = [ProductImageInline]

    def owner_status(self, obj):
        return "Registered" if obj.seller_information.user else "Guest"
    owner_status.short_description = 'Owner Status'
admin.site.register(Product, ProductAdmin)
