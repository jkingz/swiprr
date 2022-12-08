import json

from django.contrib import admin
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer
from rest_framework import serializers
from simple_history.admin import SimpleHistoryAdmin

from .models import Answer, Choice, Question, QuestionType


class Geeks(object):
    def __init__(self, json_data):
        self.json_data = json_data


class GeeksSerializer(serializers.Serializer):
    # intialize fields
    json_data = serializers.JSONField()


class QuestionAdmin(SimpleHistoryAdmin):
    list_display = ("question", "question_type", "ordering")
    filter_horizontal = ("choices",)
    list_filter = ["question_type"]
    search_fields = ["question"]


class QuestionTypeAdmin(SimpleHistoryAdmin):
    list_display = ("name", "ordering")
    search_fields = ["name"]


class AnswerGroupAdmin(SimpleHistoryAdmin):
    readonly_fields = ("answered_questions",)
    list_display = ("email", "date_answered", "is_active")
    search_fields = ["email"]

    def answered_questions(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.data, sort_keys=False, indent=2)

        # Truncate the data. Alter as needed
        response = response[:5000]

        # Get the Pygments formatter
        formatter = HtmlFormatter(style="colorful")

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    answered_questions.short_description = "data prettified"


class ChoiceAdmin(SimpleHistoryAdmin):
    search_fields = ["choice_name"]


admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionType, QuestionTypeAdmin)
admin.site.register(Answer, AnswerGroupAdmin)
admin.site.register(Choice, ChoiceAdmin)
