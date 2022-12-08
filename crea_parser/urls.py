from rest_framework import routers

from .views import CreaCeleryViewSet, CreaParserViewSet

app_name = "parser"

router = routers.SimpleRouter()

router.register(r"", CreaParserViewSet, basename="crea-parser")
router.register(r"celery", CreaCeleryViewSet, basename="crea-celery")

urlpatterns = router.urls
