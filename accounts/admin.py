from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



# Register LoginLog and Activity
@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'location', 'is_new_device', 'is_first_login', 'timestamp')
    list_filter = ('is_new_device', 'is_first_login', 'timestamp')
    search_fields = ('user__username', 'ip_address', 'location')


admin.site.site_header = "Able Administrator Page"  # Top left header
admin.site.site_title = "Able Administrator Portal"  # Title on browser tab
admin.site.index_title = "Welcome Suprime"  # Main page title