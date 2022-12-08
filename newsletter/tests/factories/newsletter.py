import factory
from django.core.files.base import ContentFile
from factory.django import ImageField
from faker import Faker
from newsletter.models import NewsLetter
from newsletter.tests.utils import produce_valid_tags
from users.tests.factories.user import UserFactory

fake = Faker()


class NewsLetterFactory(factory.django.DjangoModelFactory):
    """
    News Letter Factory
    """

    class Meta:
        model = NewsLetter

    title = factory.LazyAttribute(lambda o: fake.sentence())
    body = factory.LazyAttribute(lambda o: fake.paragraph())
    owner = factory.SubFactory(UserFactory)
    image = factory.LazyAttribute(
        lambda _: ContentFile(
            ImageField()._make_data({"width": 1024, "height": 768}), "example.jpg"
        )
    )

    @factory.post_generation
    def tags(self, create, tags, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # If no tags is passed, create random tags
        if not tags:
            tags = produce_valid_tags()

        if tags:
            # A list of groups were passed in, use them
            for tag in tags:
                self.tags.add(tag)
