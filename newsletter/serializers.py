from rest_framework import serializers

from .models import NewsLetter


class StringListField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, data):
        # you change the representation style here.
        return " ".join(data.values_list("name", flat=True))


class NewsLetterSerializer(serializers.ModelSerializer):

    tags = StringListField()

    class Meta:
        model = NewsLetter
        fields = ("title", "body", "image", "tags")

    def create(self, validated_data):
        # Override create to conform to django-taggit on how it's save
        # NOTE: Frontend does the cleaning for the "#"
        tags = validated_data.pop("tags")
        instance = super().create(validated_data)
        instance.tags.set(*tags)
        return instance

    def update(self, instance, validated_data):
        # Override create to conform to django-taggit on how it's update
        # NOTE: Frontend does the cleaning for the "#"
        tags = validated_data.pop("tags")
        instance = super().update(validated_data)
        instance.tags.set(*tags)
        return instance

    def validate(self, data):
        """
        putting owner since we didn't pass owner on the first initalization of data
        """

        data["owner"] = self.context.get("request").user
        return super().validate(data)
