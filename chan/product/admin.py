from django.contrib import admin
from .models import Product, ProductImage, CustomFieldValue
from .models import CustomField, CategoryCustomField, Category
from django import forms
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import escape

class CustomFieldForm(forms.ModelForm):
    class Meta:
        model = CustomField
        fields = '__all__'
        widgets = {
            'options': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomFieldForm, self).__init__(*args, **kwargs)
        # Initialize your field choices here, or dynamically load them in the template with JavaScript
        if 'initial' in kwargs:
            field_type = kwargs['initial'].get('field_type', None)
        else:
            field_type = self.instance.field_type if self.instance else None

        if field_type:
            self.fields['options'].widget = self.get_widget_for_field_type(field_type)

    def get_widget_for_field_type(self, field_type):
        # Return the appropriate widget based on field_type
        if field_type == 'select':
            return forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter options separated by commas'})
        elif field_type == 'checkbox':
            return forms.CheckboxSelectMultiple()
        elif field_type == 'radio':
            return forms.RadioSelect()
        # Add other conditions for different field types
        # ...
        return forms.TextInput()  # Default widget

class CategoryCustomFieldForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple("Categories", is_stacked=False)
    )

    class Meta:
        model = CategoryCustomField
        fields = '__all__'

class CategoryCustomFieldAdmin(admin.ModelAdmin):
    form = CategoryCustomFieldForm

    def save_model(self, request, obj, form, change):
        # Clear previous categories to prevent duplicates
        if change:
            obj.category.clear()
        
        # Save the custom field first
        super().save_model(request, obj, form, change)
        
        # Add the selected categories
        for category in form.cleaned_data['category']:
            CategoryCustomField.objects.create(custom_field=obj, category=category)


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    form = CustomFieldForm
    list_display = ('name', 'field_type', 'get_categories')
    list_filter = ('field_type',)
    search_fields = ('name',)
    filter_horizontal = ('categories',)

    def get_categories(self, obj):
        return ", ".join([category.title for category in obj.categories.all()])
    get_categories.short_description = 'Categories'

@admin.register(CategoryCustomField)
class CategoryCustomFieldAdmin(admin.ModelAdmin):
    list_display = ('category', 'custom_field')
    list_filter = ('category',)
    search_fields = ('custom_field__name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class CustomFieldValueInline(admin.TabularInline):
    model = CustomFieldValue
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'condition', 'created_at', 'owner_status', 'custom_fields_list')
    list_filter = ('category', 'condition')
    search_fields = ('title', 'description')
    inlines = [ProductImageInline, CustomFieldValueInline]

    def owner_status(self, obj):
        return "Registered" if obj.seller_information.user else "Guest"
    owner_status.short_description = 'Owner Status'

    def custom_fields_list(self, obj):
        # This method would display a list of custom fields and their values
        return ", ".join([f"{cfv.custom_field.name}: {cfv.value}" for cfv in obj.custom_field_values.all()])
    custom_fields_list.short_description = 'Custom Fields'

admin.site.register(Product, ProductAdmin)

