from django.contrib import admin
from .models import StudentPreferenceModel, SupportTicket
# Register your models here.
# admin.site.register(StudentPreferenceModel)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'role', 'registered_email', 'ticket_type', 'created_at', 'is_resolved')
    list_filter = ('role', 'ticket_type', 'is_resolved', 'created_at')
    search_fields = ('subject', 'message', 'user__username', 'registered_email')
    readonly_fields = ('user', 'role', 'registered_email', 'ticket_type', 'subject', 'message', 'created_at')


@admin.register(StudentPreferenceModel)
class StudentPreferenceModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'sendEmailOnLogin')
