import factory
from crea_parser.models import PropertyPhoto
from faker import Faker

from django.utils import timezone

fake = Faker()


class PropertyPhotoFactory(factory.django.DjangoModelFactory):
    """
    PropertyPhoto Factory
    """

    class Meta:
        model = PropertyPhoto

    # Assign a temporary sequence id
    sequence_id = factory.LazyAttribute(lambda o: 0)
    last_updated = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    description = factory.LazyAttribute(lambda o: fake.paragraph())

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", property_photo=None
    )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)

        # Update seqeunce to be based on property factory
        sequence_id = 1
        property_photo_list = PropertyPhoto.active_objects.filter(
            connected_property=kwargs.get("connected_property")
        ).order_by("-sequence_id")
        if property_photo_list:
            sequence_id = property_photo_list[0].sequence_id + 1
        kwargs["sequence_id"] = sequence_id

        return manager.create(*args, **kwargs)
