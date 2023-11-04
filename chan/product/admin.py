from django.contrib import admin
from .models import Category
from mptt.admin import MPTTModelAdmin

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
