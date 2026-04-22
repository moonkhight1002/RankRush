from django.contrib import admin
from .models import AuthIdentifierSettings, StudentPreferenceModel, SupportTicket
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


@admin.register(AuthIdentifierSettings)
class AuthIdentifierSettingsAdmin(admin.ModelAdmin):
    list_display = ('settings_label', 'username_mode', 'username_affix', 'affix_position', 'updated_at')
    list_display_links = ('settings_label',)
    readonly_fields = ('username_preview', 'updated_at')
    fieldsets = (
        (
            'Institute Username Format',
            {
                'fields': ('username_mode', 'username_affix', 'affix_position', 'username_preview', 'updated_at'),
                'description': (
                    'Choose whether users enter a manual username or whether the portal uses the part '
                    'before @ from their email address. Optional institute text can still be attached '
                    'before or after that username.'
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        if AuthIdentifierSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def settings_label(self, obj):
        return 'Open settings'

    settings_label.short_description = 'Settings'

    def username_preview(self, obj):
        if obj is None:
            return 'student123'
        if obj.username_mode == AuthIdentifierSettings.MODE_EMAIL_PREFIX:
            base_value = 'student123 from student123@example.com'
        else:
            base_value = 'student123'
        affix = (obj.username_affix or '').strip()
        if not affix:
            return base_value
        if obj.affix_position == AuthIdentifierSettings.POSITION_PREFIX:
            return f'{affix}{base_value}'
        return f'{base_value}{affix}'

    username_preview.short_description = 'Example username'
