from django.contrib import admin

from .models import CSDMapping, StaffMapping, ResNetInternalUser


class CSDMappingAdmin(admin.ModelAdmin):
    list_display = ('csd_domain', 'csd_alias', 'csd_name')


class StaffMappingAdmin(admin.ModelAdmin):
    list_display = ('staff_title', 'staff_alias', 'staff_name')


class ResNetInternalUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_active',
                    'is_net_admin', 'is_telecom', 'is_tag', 'is_rn_staff', 'is_technician',
                    'is_new_tech', 'orientation_complete', 'is_developer')
    list_filter = ('is_active', 'is_net_admin', 'is_telecom', 'is_tag', 'is_rn_staff',
                   'is_technician', 'is_new_tech', 'is_developer')

admin.site.register(CSDMapping, CSDMappingAdmin)
admin.site.register(StaffMapping, StaffMappingAdmin)
admin.site.register(ResNetInternalUser, ResNetInternalUserAdmin)
