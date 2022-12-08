from datetime import timedelta
from secrets import token_urlsafe
from statistics import mode

from allauth.account.models import EmailAddress
from core.models import CommonInfo
from core.utils import HomeswiprMailer
from model_utils import FieldTracker
from simple_history.models import HistoricalRecords
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import UserManager

del AbstractBaseUser.is_active  # Deletes the shadowed attribute for user table (fix for is_active issue)


class User(AbstractBaseUser, PermissionsMixin, CommonInfo):
    """
    overriding user model
    """

    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    phone_number = models.CharField(
        _("phone number"), max_length=15, blank=True, null=True
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_(
            "This does not create a new email on Account application, which is needed in the login. "
            "If you want to create a user that can login through. Create through the Account Email table"
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_agent = models.BooleanField(
        _("agent"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    is_user_manager = models.BooleanField(
        default=False,
        help_text=_(
            "Designates whether this user can access the homeswiper user manager interface."
        ),
    )

    # Field for assigning multiple agents.
    agents = models.ManyToManyField(
        'users.User', blank=True, related_name="assigned_agents"
    )

    # Referral part for the user
    referral_code = models.CharField(max_length=124)

    referral_code_expiry_date = models.DateTimeField(
        _("referral expired token"), default=timezone.now
    )

    user_type = models.ForeignKey('users.UserType', on_delete=models.SET_NULL, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name")

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.email}"

    def validate_user(self):
        email = self.email
        phone_number = self.phone_number
        if email:
            if User.objects.filter(email=email).exists():
                if self.tracker.has_changed('email') and self.tracker.previous('email') != self.email:
                    raise ValidationError({"email": "Email already exists"})
        if phone_number:
            if User.objects.filter(phone_number=phone_number).exists():
                if self.tracker.has_changed('phone_number') and \
                        self.tracker.previous('phone_number') != self.phone_number:
                    raise ValidationError({"phone_number": "Phone number already exists"})
        if not (email or phone_number):
            raise ValidationError({"user": "Please provide email or phone number"})

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        self.validate_user()
        if not self.id:
            self.handle = self.trimmed_email
            self.generate_referral_code()

        return super(User, self).save(*args, **kwargs)

    def get_short_name(self):
        return f"{self.first_name}"

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".title()

    @property
    def get_display_name(self):
        if self.first_name and self.last_name:
            return self.get_full_name
        return f"{self.email}"

    @property
    def trimmed_email(self):
        return self.email.split("@")[0]

    @property
    def is_referral_code_expired(self):
        if self.referral_code_expiry_date < timezone.now():
            return True
        return False

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def generate_referral_code(self):
        # Generating secure token using python libraries
        not_found = True
        while not_found:
            new_token = token_urlsafe(64)
            if not User.objects.filter(referral_code=new_token):
                self.referral_code = new_token
                self.referral_code_expiry_date = timezone.now() + timedelta(days=7)
                not_found = False

    def get_initials(fullname):
        xs = (fullname)
        name_list = xs.split()

        initials = ""

        for name in name_list:  # go through each name
            initials += name[0].upper()  # append the initial

        return initials


class UserRegistrationInformation(CommonInfo):
    """
    A model to save the user registraton information.

    Currently used to only save apple information.
    As for the why: here is a snippet from one of their engineers:
    https://developer.apple.com/forums/thread/121496

    TLDR: Apple only sents the user information on the first sign up

    Some sample why a registration can fail: (Not accepting the EULA
    on the first try, A slow internet connection (Apple only has 5 minute expiry token))
    """

    NONE = 0
    APPLE = 1

    SOCIAL_APPLICATION_CHOICES = ((NONE, "none"), (APPLE, "apple"))

    social_application = models.IntegerField(
        choices=SOCIAL_APPLICATION_CHOICES, default=0
    )

    # Also save raw json, to catch any updates we need to catch
    raw_json = JSONField()

    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    phone_number = models.CharField(
        _("phone number"), max_length=15, blank=True, null=True
    )
    email = models.EmailField(
        _("email address"),
        help_text=_(
            "This does not create a new email on Account application, which is needed in the homeswipr login. "
            "If you want to create a user that can login through homeswipr. Create through the Account Email table"
        ),
        blank=True,
        null=True,
    )

    def __str__(self, *args, **kwargs):
        return f"{self.email} - {self.get_social_application_display()}"


class Referral(CommonInfo):

    invited_user = models.OneToOneField(
        User, on_delete=models.PROTECT, related_name="invited_user", unique=True
    )

    referred_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="referred_by"
    )

    unique_together = ["invited_user", "referred_by"]

    def __str__(self, *args, **kwargs):
        return f"{self.invited_user} referred by {self.referred_by}"


class UserHistory(CommonInfo):
    """
    Saves all the user history in our database
    """

    UNDEFINED = 0
    VIEWED = 1

    HISTORY_TYPE = [(UNDEFINED, "undefined"), (VIEWED, "viewed")]

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user_history"
    )
    history_type = models.IntegerField(choices=HISTORY_TYPE, default=UNDEFINED)

    # The generic foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.user} {self.get_history_type(self.history_type)} '{self.content_object}'"

    @classmethod
    def get_history_type(cls, id):
        return dict(cls.HISTORY_TYPE).get(id)

    class Meta:
        verbose_name_plural = "User Histories"


class HomeswiprEmailAddress(EmailAddress):
    """
    Proxies email address from all auth.

    We should use this on our codebase rather than direcly importing
    allauth's email address. This should keep make the all_auth's EmailAddress
    more manageable.
    """

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):

        # Removes other email address, to keep only one email address
        # in our system
        other_emails = HomeswiprEmailAddress.objects.filter(user=self.user).exclude(
            email=self.email
        )

        if other_emails:
            for email in other_emails:
                email.delete()

        # Since we are deleting other emails, make this always the primary
        self.primary = True

        return super().save(*args, **kwargs)


class HomeswiprLead(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    agents = models.ManyToManyField(
        'users.User', related_name="leads_agents_set", blank=True
    )

    def __str__(self):
        return self.email


class HomeswiprMail(models.Model):
    email = models.ForeignKey(
        "HomeswiprLead", on_delete=models.CASCADE, related_name="homeswipr_leads"
    )
    file = models.FileField(upload_to="mails/", blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    date_sent = models.DateTimeField(default=timezone.now)

    def __str__(self):
        try:
            return self.file_url.split("/")[-1]
        except Exception as e:
            return "(empty file name)"

    def save(self, *args, **kwargs):
        if self.file:
            self._send_mail()
            self.file_url = self.file.url

        super(HomeswiprMail, self).save(*args, **kwargs)

    def _send_mail(self):
        mail = HomeswiprMailer(
            subject="Homeswipr-Estimates",
            recipient=self.email.email,
            html_template="homeswipr/email/estimate_email.html",
            text_template="homeswipr/email/estimate_email.txt",
            attachment=self.file,
            context={"email": self.email.email},
        )
        mail.send_mail()


class UserType(CommonInfo):
    """
    Model for account user type.
    """
    type = models.CharField(_("User Type"), max_length=100, unique=True)

    def __str__(self):
        return f"{self.type}"
