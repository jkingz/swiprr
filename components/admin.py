from django.contrib import admin

from .models import (
    Brokerage,
    Agent,
    LawFirm,
    GoodsIncluded,
    Conditions,
    ConditionStatus,
    AdditionalTerms,
    PaymentMethod,
    PropertyType,
    Attachments,
    UnreadNote,
    Email,
    PhoneNumber
)


class BrokerageAdmin(admin.ModelAdmin):
    search_fields = ["name", "email", "phone_number", "fax_number"]


class AgentAdmin(admin.ModelAdmin):
    search_fields = ["full_name", "first_name", "last_name", "email", "phone_number", "fax_number"]


class LawFirmAdmin(admin.ModelAdmin):
    search_fields = ["lawyer_name", "name", "address", "email", "phone_number", "fax_number"]


class GoodsIncludedAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class ConditionsAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class ConditionStatusAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class AdditionalTermsAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class PaymentMethodAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class PropertyTypeAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class AttachmentsAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class UnreadNoteAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__last_name", "last_date_viewed"]


class EmailAdmin(admin.ModelAdmin):
    search_fields = ["email"]


class PhoneNumberAdmin(admin.ModelAdmin):
    search_fields = ["phone_number"]


admin.site.register(Brokerage, BrokerageAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(LawFirm, LawFirmAdmin)
admin.site.register(GoodsIncluded, GoodsIncludedAdmin)
admin.site.register(Conditions, ConditionsAdmin)
admin.site.register(ConditionStatus, ConditionStatusAdmin)
admin.site.register(AdditionalTerms, AdditionalTermsAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(PropertyType, PropertyTypeAdmin)
admin.site.register(Attachments, AttachmentsAdmin)
admin.site.register(UnreadNote, UnreadNoteAdmin)
admin.site.register(Email, UnreadNoteAdmin)
admin.site.register(PhoneNumber, UnreadNoteAdmin)
