from django.contrib import admin
from .models import Country, City, Address

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)
    list_filter = ('country',)
    autocomplete_fields = ['country']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('line1', 'line2', 'zip_code', 'city')
    search_fields = ('line1', 'city__name')
    list_filter = ('city',)
    autocomplete_fields = ['city']
