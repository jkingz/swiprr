from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    HomeswiprLead,
    HomeswiprMail,
    Referral,
    User,
    UserHistory,
    UserRegistrationInformation,
    UserType
)


class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "date_created", "object_id")
    list_filter = ("is_active",)


class UserHashableAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_agent",
                    "is_user_manager",
                    "user_type",
                    "groups",
                    "user_permissions",
                    "referral_code",
                    "referral_code_expiry_date",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


class ReferralAdmin(admin.ModelAdmin):
    search_fields = ["invited_user__email", "referred_by__email"]


class UserRegistrationAdmin(admin.ModelAdmin):
    list_filter = ["is_active"]
    search_fields = ["first_name", "last_name", "phone_number", "email"]


class HomeswiprLeadAdmin(admin.ModelAdmin):
    pass


class HomeswiprMailsAdmin(admin.ModelAdmin):
    pass


class UserTypeAdmin(admin.ModelAdmin):
    search_fields = ['type']


admin.site.register(UserRegistrationInformation, UserRegistrationAdmin)
admin.site.register(User, UserHashableAdmin)
admin.site.register(Referral, ReferralAdmin)
admin.site.register(UserHistory, UserHistoryAdmin)
admin.site.register(HomeswiprLead, HomeswiprLeadAdmin)
admin.site.register(HomeswiprMail, HomeswiprMailsAdmin)
admin.site.register(UserType, UserTypeAdmin)
