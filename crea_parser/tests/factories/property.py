import factory
from crea_parser.models import Property
from crea_parser.tests.factories.address import PropertyAddressFactory
from crea_parser.tests.factories.agent import AgentFactory
from crea_parser.tests.factories.alternate_url import AlternateUrlFactory
from crea_parser.tests.factories.building import BuildingFactory
from crea_parser.tests.factories.geolocation import GeoLocationFactory
from crea_parser.tests.factories.land import LandFactory
from crea_parser.tests.factories.parking import ParkingFactory
from crea_parser.tests.factories.property_info import PropertyInfoFactory
from crea_parser.tests.factories.property_photo import PropertyPhotoFactory
from crea_parser.tests.factories.room import RoomFactory
from crea_parser.tests.factories.utility import UtilityFactory
from django.utils import timezone
from faker import Faker

fake = Faker()


class PropertyFactory(factory.django.DjangoModelFactory):
    """
    Property Factory
    """

    class Meta:
        model = Property

    # Using bank number. We could change this if we could fake a more suitable fake
    ddf_id = factory.Sequence(lambda o: f"{fake.bban()}-{o}")
    # Need to check other values, currently ddf is the only thing we can see on local
    listing_type = factory.LazyAttribute(lambda o: 1)
    creation_date = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )
    last_updated = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )

    link = factory.LazyAttribute(lambda o: fake.url())
    full_address = factory.LazyAttribute(lambda o: fake.address())
    unit_number = factory.LazyAttribute(lambda o: fake.building_number())
    street_number = factory.LazyAttribute(lambda o: fake.building_number())
    street_name = factory.LazyAttribute(lambda o: fake.street_name())
    postal_code = factory.LazyAttribute(lambda o: fake.postcode())

    multi = factory.LazyAttribute(lambda o: fake.boolean())
    status = factory.LazyAttribute(lambda o: "active")
    # # Also need to check if there's other attributes other than 1
    next_image_id = factory.LazyAttribute(lambda o: 1)
    expiry_date = factory.LazyAttribute(
        lambda o: fake.future_datetime(tzinfo=timezone.get_current_timezone())
    )
    listing_id = factory.Sequence(lambda o: f"{fake.bban()}-{o}")
    # # Still need to check if other attributes other than 0 exists
    reminder_count = factory.LazyAttribute(lambda o: 0)
    is_active = True

    property_info = factory.RelatedFactory(
        PropertyInfoFactory,
        factory_related_name="connected_property",
        price=factory.LazyAttribute(
            lambda o: fake.pydecimal(right_digits=2, max_value=100000000000)
        ),
    )

    address = factory.RelatedFactory(
        PropertyAddressFactory, factory_related_name="connected_property"
    )

    agent = factory.RelatedFactory(AgentFactory, factory_related_name="connected_property")

    building = factory.RelatedFactory(BuildingFactory, factory_related_name="connected_property")

    alternate_url = factory.RelatedFactory(
        AlternateUrlFactory, factory_related_name="connected_property"
    )

    geo_location = factory.RelatedFactory(
        GeoLocationFactory, factory_related_name="connected_property"
    )

    land = factory.RelatedFactory(LandFactory, factory_related_name="connected_property")

    parking = factory.RelatedFactory(ParkingFactory, factory_related_name="connected_property")

    property_photo = factory.RelatedFactory(
        PropertyPhotoFactory, factory_related_name="connected_property"
    )

    room = factory.RelatedFactory(RoomFactory, factory_related_name="connected_property")

    utility = factory.RelatedFactory(UtilityFactory, factory_related_name="connected_property")
