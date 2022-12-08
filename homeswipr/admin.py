from django.contrib import admin

from .models import (
    AgentFavorite,
    Brokerage,
    FrequentlyAskedQuestion,
    LawFirm,
    PropertyFavorite,
    PropertyInquiry,
    UserSavedSearch,
    Agent
)


class PropertyFavoriteAdmin(admin.ModelAdmin):
    autocomplete_fields = ("favorited_property",)
    search_fields = (
        "favorited_property__listing_id",
        "favorited_property__ddf_id",
    )
    list_display = ("__str__", "user")
    list_filter = ("is_active",)


class AgentFavoriteAdmin(admin.ModelAdmin):
    autocomplete_fields = ("favorited_agent",)
    list_display = ("favorited_agent", "user")
    list_filter = ("is_active",)
    search_fields = ["favorited_agent__name"]


class UserSavedSearchAdmin(admin.ModelAdmin):
    readonly_fields = ("last_checked_date",)
    list_filter = ("is_active",)
    search_fields = ["title", "search_text", "user__email"]


class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):
    list_filter = ("is_active",)
    search_fields = ["question", "answer"]


class PropertyInquiryAdmin(admin.ModelAdmin):
    list_filter = ["status"]
    search_fields = ["first_name", "last_name", "email", "phone_number", "question"]


class PropertyOfferAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    filter_horizontal = (
        'agents',
    )
    list_filter = ["status"]
    search_fields = ["offer_amount", "deposit_date", "deposit_amount"]


class OfferConditionAdmin(admin.ModelAdmin):
    search_fields = ["condition_date", "name"]


class OfferAdditionalTermAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class OfferGoodsIncludedAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class OfferBuyerAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "email", "phone_number", "company_name"]


class BrokerageAdmin(admin.ModelAdmin):
    search_fields = ["name", "email", "phone_number"]


class LawFirmAdmin(admin.ModelAdmin):
    search_fields = ["lawyer_name", "name", "address", "email", "phone_number"]


class AgentAdmin(admin.ModelAdmin):
    search_fields = ["full_name", "first_name", "last_name", "email", "phone_number"]


admin.site.register(PropertyInquiry, PropertyInquiryAdmin)
admin.site.register(PropertyFavorite, PropertyFavoriteAdmin)
admin.site.register(AgentFavorite, AgentFavoriteAdmin)
admin.site.register(UserSavedSearch, UserSavedSearchAdmin)
admin.site.register(FrequentlyAskedQuestion, FrequentlyAskedQuestionAdmin)
admin.site.register(Brokerage, BrokerageAdmin)
admin.site.register(LawFirm, LawFirmAdmin)
admin.site.register(Agent, AgentAdmin)
