from django.contrib import admin

from contacts.models import (
    Contact,
    Note,
    ContactAgent,
    ContactMortgageBroker,
    ContactSalesAgent
)


class ContactAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "middle_name", "email", "phone_number",
                     "city", "associated_company", "occupation", "source"]


class ContactAgentAdmin(admin.ModelAdmin):
    search_fields = ["contact__first_name", "contact__middle_name", "contact__last_name", "contact__email",
                     "agent__full_name", "agent__first_name", "agent__last_name", "agent__email"]


class NoteAdmin(admin.ModelAdmin):
    search_fields = ["note", "contact__first_name", "contact__middle_name", "contact__last_name",
                     "contact__email", "created_by__first_name", "created_by__last_name", "created_by__email"]


class ContactMortgageBrokerAdmin(admin.ModelAdmin):
    search_fields = ["contact__first_name", "contact__middle_name", "contact__last_name", "contact__email",
                     "mortgage_broker__first_name", "mortgage_broker__last_name", "mortgage_broker__email"]


class ContactSalesAgentAdmin(admin.ModelAdmin):
    search_fields = ["contact__first_name", "contact__middle_name", "contact__last_name", "contact__email",
                     "sales_agent__first_name", "sales_agent__last_name", "sales_agent__email"]


admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactAgent, ContactAgentAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(ContactMortgageBroker, ContactMortgageBrokerAdmin)
admin.site.register(ContactSalesAgent, ContactSalesAgentAdmin)
