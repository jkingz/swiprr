from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from deal.models import (
    AdditionalTerm,
    Brokerage,
    Client,
    Commission,
    Condition,
    Deal,
    DealStatus,
    Deposit,
    GoodsIncluded,
    LawFirm,
    Realtor
)


class AdditionalTermAdmin(admin.ModelAdmin):
    search_fields = ["name", "note"]


class ClientAdmin(admin.ModelAdmin):
    list_filter = ["client_type"]
    search_fields = ["client__first_name", "client__last_name", "client__email", "client__phone_number"]


class BrokerageAdmin(admin.ModelAdmin):
    list_filter = ["representing"]
    search_fields = ["brokerage__name", "brokerage__email", "brokerage__phone_number"]


class CommissionAdmin(admin.ModelAdmin):
    list_filter = ["type"]
    search_fields = ["agent__first_name", "agent__last_name", "agent__email", "percentage", "total"]


class ConditionAdmin(admin.ModelAdmin):
    search_fields = ["name", "status", "date"]


class DealAdmin(admin.ModelAdmin):
    list_filter = ["representing", "status", "property_type", "is_conveyancing"]
    search_fields = ["possession_date", "sale_price", "sale_date", "address",
                     "created_by__first_name", "created_by__last_name"]


class DealStatusAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class DepositAdmin(admin.ModelAdmin):
    list_filter = ["is_additional"]
    search_fields = ["amount", "date", "payment_method"]


class GoodsIncludedAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class LawFirmAdmin(admin.ModelAdmin):
    list_filter = ["representing"]
    search_fields = ["lawfirm__lawyer_name", "lawfirm__name", "lawfirm__address",
                     "lawfirm__email", "lawfirm__phone_number"]


class RealtorAdmin(admin.ModelAdmin):
    list_filter = ["representing"]
    search_fields = ["agent__first_name", "agent__last_name", "agent__email", "agent__phone_number"]


admin.site.register(AdditionalTerm, AdditionalTermAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Brokerage, BrokerageAdmin)
admin.site.register(Commission, CommissionAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(Deal, DealAdmin)
admin.site.register(DealStatus, DealStatusAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(GoodsIncluded, GoodsIncludedAdmin)
admin.site.register(LawFirm, LawFirmAdmin)
admin.site.register(Realtor, RealtorAdmin)
