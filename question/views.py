from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import HomeswiprLead
from users.permissions import IsUserManager

from .models import Answer, Question, QuestionType
from .serializers import AnswerSerializer, QuestionSerializer, QuestionTypeSerializer


class QuestionViewSet(viewsets.ModelViewSet):

    # permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerializer
    pagination_class = None
    queryset = Question.objects.filter(is_active=True).order_by("ordering", "question_type__ordering")

    @action(detail=False, methods=["get"])
    def get_count(self, request):
        questions_count = self.get_queryset().count()
        return Response({"count": questions_count}, status=status.HTTP_200_OK)


class QuestionTypeViewSet(viewsets.ModelViewSet):

    pagination_class = None
    queryset = QuestionType.objects.all().order_by("ordering")
    serializer_class = QuestionTypeSerializer

    @action(detail=False, methods=["get"])
    def get_questions(self, request):
        question_types = self.get_queryset().order_by('ordering')
        _questions = []

        for question_type in question_types:
            question = {
                'id': question_type.id,
                'name': question_type.name,
                'ordering': question_type.ordering,
                'questions': question_type.question_set.all().values()
            }
            _questions.append(question)
        return Response(_questions, status=status.HTTP_200_OK)


class AnswerViewSet(viewsets.ModelViewSet):

    queryset = Answer.objects.all().order_by("date_answered")
    serializer_class = AnswerSerializer

    @action(
        detail=False,
        methods=["get"],
        permission_classes=(IsAuthenticated, IsUserManager),
    )
    def get_answers_from_lead_profile(self, request, **kwargs):
        fk_email_id = self.request.query_params.get("fk_email_id", None)

        answers = Answer.objects.filter(fk_email__id=fk_email_id)

        serializer = self.get_serializer(answers, many=True)
        response = Response(serializer.data)

        return response
