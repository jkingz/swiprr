from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class ActiveManager(models.Manager):
    """
    This class defines a new default query set so the project can always
        filter data that is active
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class CommonInfo(models.Model):
    """
    This class is the parent class for all the models
    """

    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # This allows me to escape to default django query set if
    #   later in the project I need it
    objects = models.Manager()

    # for active query set
    active_objects = ActiveManager()

    class Meta:
        abstract = True


class ContactInfo(models.Model):
    """
    This class is intendent 
    """

    email = models.EmailField(max_length=225, null=True, blank=True)
    phone_number = models.CharField(max_length=50,  null=True, blank=True)
    fax = models.CharField(max_length=50,  null=True, blank=True)

    # This allows me to escape to default django query set if
    #   later in the project I need it
    objects = models.Manager()

    # for active query set
    active_objects = ActiveManager()

    class Meta:
        abstract = True
