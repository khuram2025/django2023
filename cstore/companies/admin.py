from django.contrib import admin
from .models import CompanyProfile, Branch, PhoneNumber, Schedule

class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'owner', 'verified', )
    search_fields = ('name', 'owner__full_name', 'owner__mobile')
    list_filter = ('verified',)

admin.site.register(CompanyProfile, CompanyProfileAdmin)

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1

class BranchAdmin(admin.ModelAdmin):
    inlines = [ScheduleInline]

admin.site.register(Branch, BranchAdmin)



admin.site.register(PhoneNumber)
