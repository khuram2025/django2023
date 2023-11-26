from django.contrib import admin
from .models import CompanyProfile, Branch, Location, PhoneNumber, Schedule

class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'verified')
    search_fields = ('name', 'owner__full_name', 'owner__mobile')
    list_filter = ('verified',)

admin.site.register(CompanyProfile, CompanyProfileAdmin)

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1

class BranchAdmin(admin.ModelAdmin):
    inlines = [ScheduleInline]

admin.site.register(Branch, BranchAdmin)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'branch', 'address')
   
    search_fields = ('city__name', 'branch__name', 'address')

    def city_name(self, obj):
        return obj.city.name
    city_name.admin_order_field = 'city__name'  # Allows column order sorting
    city_name.short_description = 'City'       # Column header

admin.site.register(PhoneNumber)
