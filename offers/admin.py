from django.contrib import admin

from .models import (
    Offer,
    OfferStatus,
    OfferClient,
    OfferAgent,
    OfferNote,
    Requirement,
    Condition,
    AdditionalTerm,
    Deposit,
    GoodsIncluded,
    OfferAdditionalDocuments
)


class OfferAdmin(admin.ModelAdmin):
    list_filter = ["representing", "offer_status", "property_type"]
    search_fields = ["address", "offer_amount", "offer_open_till", "created_by__first_name", "created_by__last_name"]


class OfferStatusAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class OfferClientAdmin(admin.ModelAdmin):
    list_filter = ["type"]
    search_fields = ["client__first_name", "client__last_name", "first_name", "last_name"]


class OfferAgentAdmin(admin.ModelAdmin):
    list_filter = ["representing"]
    search_fields = ["agent__first_name", "agent__last_name"]


class OfferNoteAdmin(admin.ModelAdmin):
    search_fields = ["note", "created_by__first_name", "created_by__last_name"]


class OfferAdditionalDocumentsAdmin(admin.ModelAdmin):
    search_fields = ["name", "created_by__first_name", "created_by__last_name"]


class RequirementAdmin(admin.ModelAdmin):
    search_fields = ["note"]


class ConditionAdmin(admin.ModelAdmin):
    list_filter = ["status"]
    search_fields = ["name", "condition_date"]


class AdditionalTermAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class DepositAdmin(admin.ModelAdmin):
    list_filter = ["is_additional"]
    search_fields = ["deposit_amount", "deposit_date", "payment_method"]


class GoodsIncludedAdmin(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferStatus, OfferStatusAdmin)
admin.site.register(OfferClient, OfferClientAdmin)
admin.site.register(OfferAgent, OfferAgentAdmin)
admin.site.register(OfferNote, OfferNoteAdmin)
admin.site.register(OfferAdditionalDocuments, OfferAdditionalDocumentsAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(AdditionalTerm, AdditionalTermAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(GoodsIncluded, GoodsIncludedAdmin)
