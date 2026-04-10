from django.contrib import admin
from .models import AuditAuditlog

@admin.register(AuditAuditlog)
class AuditAuditlogAdmin(admin.ModelAdmin):
    list_display = ('action', 'action_details', 'module', 'performed_by_id', 'created_at')
    list_filter = ('module', 'performed_by_id',)
    search_fields = ('action', 'action_details',)