from rest_framework import routers

from .views import AnswerViewSet, QuestionTypeViewSet, QuestionViewSet

router = routers.SimpleRouter()
router.register(r"questions", QuestionViewSet)
router.register(r"question-types", QuestionTypeViewSet)
router.register(r"answers", AnswerViewSet)

urlpatterns = router.urls
