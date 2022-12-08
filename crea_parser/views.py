from celery.task.control import revoke
from core.celery import app
from core.pagination import StandardResultsSetPagination
from core.permissions import IsSuperUser
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .tasks import fetch_ddf_listings


class CreaParserViewSet(ViewSet, GenericAPIView):
    """
    Manually Trigger Fetch CREA/DDF Data
    """

    permission_classes = (IsSuperUser,)
    pagination_class = StandardResultsSetPagination

    def create(self, *args, **kwargs):
        # Celery Listing ASync
        fetch_ddf_listings.delay()

        return Response(
            {"status": "Task is in queue, check the boards for information"},
            status=status.HTTP_200_OK,
        )


class CreaCeleryViewSet(ViewSet):
    """
    The viewset that lets us control the celery views
    """

    permission_classes = (IsSuperUser,)

    def list(self, *args, **kwargs):
        # Fetching running async tasks
        inspector = app.control.inspect()

        tasks = {}

        tasks["active"] = inspector.active()
        tasks["reserved"] = inspector.reserved()
        tasks["scheduled"] = inspector.scheduled()

        return Response(tasks, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def cancel(self, *args, **kwargs):
        # Cancel running async tasks
        task_id = self.request.data.get("task_id", "")
        revoke(task_id, terminate=True)
        inspector = app.control.inspect()

        tasks = {}

        tasks["active"] = inspector.active()
        tasks["reserved"] = inspector.reserved()
        tasks["scheduled"] = inspector.scheduled()

        return Response(tasks, status=status.HTTP_200_OK)
