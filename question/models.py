from django.contrib.postgres.fields import JSONField
from django.db import models
from simple_history.models import HistoricalRecords

OPTIONAL = {"blank": True, "null": True}


class Question(models.Model):
    question = models.TextField()
    choices = models.ManyToManyField("Choice", verbose_name="Choices")
    question_type = models.ForeignKey(
        "QuestionType", on_delete=models.CASCADE, **OPTIONAL
    )
    field_type = models.CharField(max_length=255)
    ordering = models.IntegerField(**OPTIONAL)
    multiple_answers = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["ordering", "question_type"]

    def __str__(self):
        return self.question


class QuestionType(models.Model):
    name = models.CharField(max_length=255)
    ordering = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        ordering = ["ordering"]

    def __str__(self):
        return self.name


class Choice(models.Model):
    choice_name = models.TextField()
    history = HistoricalRecords()

    def __str__(self):
        return self.choice_name


class Answer(models.Model):
    email = models.CharField(max_length=128)  # TODO: Remove later
    fk_email = models.ForeignKey(
        "users.HomeswiprLead", on_delete=models.CASCADE, **OPTIONAL
    )
    data = JSONField(**OPTIONAL)
    date_answered = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.email
