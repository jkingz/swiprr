import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from faker import Faker
from users.models import HomeswiprEmailAddress

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """
    User Factory
    """

    class Meta:
        model = get_user_model()

    email = factory.Sequence(
        lambda o: f"{fake.first_name()}{fake.last_name()}{o}@{fake.free_email_domain()}".lower()
    )

    first_name = factory.LazyAttribute(lambda o: fake.first_name())
    last_name = factory.LazyAttribute(lambda o: fake.last_name())
    password = make_password("password")

    is_superuser = False
    is_staff = False
    is_user_manager = False

    class Params:
        # declare a trait that adds relevant parameters for admin users
        is_admin = factory.Trait(is_superuser=True, is_staff=True)

    @factory.post_generation
    def email_address_creation_and_verification(user, create, extracted, **kwargs):
        # This will automatically verify email for ease of tests
        if not create:
            return

        email = HomeswiprEmailAddress(
            user=user, email=user.email, verified=True, primary=True
        )
        email.save()

        return
