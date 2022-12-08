from allauth.account.adapter import DefaultAccountAdapter
from core.mixins import FrontendUrlConstructionMixin
from django.contrib.sites.models import Site


class HomeSwiperAccountAdapter(DefaultAccountAdapter, FrontendUrlConstructionMixin):
    def render_mail(self, template_prefix, email, context):
        """
        Renders an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        context["current_site"] = self.frontend_base_url
        context["email"] = email
        context["activate_url"] = self.get_activation_url(context["key"])
        context["root_url"] = Site.objects.get_current().domain
        return super().render_mail(template_prefix, email, context)
