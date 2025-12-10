from django.contrib import admin
from .models import Organization, OrganizationMember

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('org_name', 'org_creator', 'org_code', 'created_on')

class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'user', 'role', 'date_joined')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationMember, OrganizationMemberAdmin)
