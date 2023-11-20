from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('mobile','full_name', 'email', 'is_staff', 'is_superuser')  # Assuming these fields exist in your model
    list_filter = ('is_staff', 'is_superuser')  # Remove 'is_active' if it was previously included
    search_fields = ('mobile', 'email')
    ordering = ('mobile',)
    fieldsets = (
        (None, {'fields': ('mobile', 'full_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    # Since we have custom fields, we need to define which fields are included in the form.
    # The UserAdmin has some defaults we might not want, so we define our own.
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

admin.site.register(CustomUser, CustomUserAdmin)
