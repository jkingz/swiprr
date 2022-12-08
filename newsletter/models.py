from core.models import CommonInfo
from django.contrib.auth import get_user_model
from django.db import models
from taggit.managers import TaggableManager


class NewsLetter(CommonInfo):
    """
    News letter model
    """

    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="news_letter")
    # If admin side tries to delete the user, raise integity error (owner is protected). We must never
    # delete a user with a newsletter! Otherwise the owner would be None, which is just strange.
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="user"
    )
    tags = TaggableManager()

    def __str__(self, *args, **kwargs):
        return f"{self.title}"


class NewsLetterSubscribe(CommonInfo):
    """
    Subscribe model
    """

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self, *args, **kwargs):
        return f"{self.name} is a subscriber"
