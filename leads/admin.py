from django.contrib import admin

from leads.models import (
    Lead,
    LeadContact,
    LeadAgents,
    LeadStatus,
    FinancialStatus,
    ContactType,
    Note,
    TimeFrame,
    LeadWarmth,
    LeadMortgageBroker,
    LeadSalesAgent
)


class LeadAdmin(admin.ModelAdmin):
    list_filter = ["transaction_type", "financial_status", "lead_status", "contact_type", "lead_warmth"]
    search_fields = ["cma_file_link", "cma_file_link", "created_by__first_name",
                     "created_by__last_name", "property_address"]


class LeadContactAdmin(admin.ModelAdmin):
    search_fields = ["contact__first_name", "contact__last_name", "contact__email", "contact__phone_number"]


class LeadAgentsAdmin(admin.ModelAdmin):
    search_fields = ["agent_assigned__first_name", "agent_assigned__last_name",
                     "agent_assigned__email", "agent_assigned__phone_number"]


class LeadStatusAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class FinancialStatusAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class ContactTypeAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class NoteAdmin(admin.ModelAdmin):
    search_fields = ["note"]


class TimeFrameAdmin(admin.ModelAdmin):
    search_fields = ["range", "index"]


class LeadWarmthAdmin(admin.ModelAdmin):
    search_fields = ["name", "index"]


class LeadMortgageBrokerAdmin(admin.ModelAdmin):
    search_fields = ["mortgage_broker__first_name", "mortgage_broker__last_name",
                     "mortgage_broker__email", "mortgage_broker__phone_number"]


class LeadSalesAgentAdmin(admin.ModelAdmin):
    search_fields = ["sales_agent__first_name", "sales_agent__last_name",
                     "sales_agent__email", "sales_agent__phone_number"]


admin.site.register(Lead, LeadAdmin)
admin.site.register(LeadContact, LeadContactAdmin)
admin.site.register(LeadAgents, LeadAgentsAdmin)
admin.site.register(LeadStatus, LeadStatusAdmin)
admin.site.register(FinancialStatus, FinancialStatusAdmin)
admin.site.register(ContactType, ContactTypeAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(TimeFrame, TimeFrameAdmin)
admin.site.register(LeadWarmth, LeadWarmthAdmin)
admin.site.register(LeadMortgageBroker, LeadMortgageBrokerAdmin)
admin.site.register(LeadSalesAgent, LeadSalesAgentAdmin)
