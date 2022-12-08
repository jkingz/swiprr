from rest_framework import serializers
from users.models import HomeswiprLead

from .models import Answer, Choice, Question, QuestionType


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = "__all__"


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.StringRelatedField(many=True, read_only=True)
    question_type = serializers.SlugRelatedField(read_only=True, slug_field="ordering")

    class Meta:
        model = Question
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"

    def validate(self, data):
        try:
            lead_place_holder = {}
            if "full_name" in data.keys():
                lead_place_holder.update({"full_name": data["full_name"]})
            if "email" in data.keys():
                lead_place_holder.update({"email": data["email"]})
            if "phone_number" in data.keys():
                lead_place_holder.update({"phone_number": data["phone_number"]})

            lead_instance = HomeswiprLead.objects.get_or_create(**lead_place_holder)[0]
            data.update({"fk_email": lead_instance})

            return data
        except Exception as e:
            return serializers.ValidationError(str(e))
