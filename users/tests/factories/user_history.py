from random import randint

import factory
from crea_parser.tests.factories.property import PropertyFactory
from django.contrib.contenttypes.models import ContentType
from users.models import UserHistory


class UserHistoryFactory(factory.django.DjangoModelFactory):

    user = None
    history_type = factory.LazyAttribute(
        lambda o: f"{randint(0, len(UserHistory.HISTORY_TYPE)-1)}"
    )
    object_id = factory.SelfAttribute("content_object.id")
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )

    class Meta:
        exclude = ["content_object"]
        abstract = True


class UserPropertyHistoryFactory(UserHistoryFactory):

    # This should avoid recursive import when customizing the fields
    # for property using the same factory

    content_object = factory.SubFactory(PropertyFactory)

    class Meta:
        model = UserHistory
