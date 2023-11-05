from django.contrib import admin
from .models import Category, Product
from mptt.admin import MPTTModelAdmin
from .models import Country, Region, City

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'seo_title', 'seo_description', 'seo_keywords']
    search_fields = ['name', 'seo_keywords']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'description', 'seo_title', 'seo_description', 'seo_keywords']
    list_filter = ['country']
    search_fields = ['name', 'country__name', 'seo_keywords']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'description', 'seo_title', 'seo_description', 'seo_keywords']
    list_filter = ['region']
    search_fields = ['name', 'region__name', 'region__country__name', 'seo_keywords']
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'condition', 'country', 'region', 'city', 'seller_information', 'created_at']
    list_filter = ['category', 'condition', 'country', 'region', 'city', 'price']
    search_fields = ['title', 'description', 'category__name', 'seller_information__name', 'seo_keywords']
    raw_id_fields = ['category', 'country', 'region', 'city', 'seller_information']
    prepopulated_fields = {"seo_keywords": ("title",)}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city":
            kwargs["queryset"] = City.objects.filter(region__isnull=False)
        elif db_field.name == "region":
            kwargs["queryset"] = Region.objects.filter(country__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('title', 'parent', 'status', 'is_subcategory', 'is_root_category')
    list_filter = ('status', 'parent')
    search_fields = ('title', 'description')

    # This will help in easily navigating through nested categories
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Category.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Optional: Customize the way categories are displayed in a hierarchy
    # Example method for Django admin to display hierarchy
    def get_title(self, obj):
        return " -> ".join([c.title for c in obj.get_ancestors(include_self=True)])
    get_title.short_description = 'Category Hierarchy'

    get_title.admin_order_field = 'title'  # Allows column order sorting

   

    list_display = ('get_title', 'status', 'is_subcategory', 'is_root_category')

