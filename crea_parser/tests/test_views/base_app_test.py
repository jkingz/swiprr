from celery.task.control import revoke
from core.celery import app
from core.tests.base_test import BaseWebTestCases


class CreaParserBaseTest(BaseWebTestCases):

    app_name = "parser"

    def revoke_all_celery_task(self):
        # Revokes all celery task for testing
        app.control.purge()

        inspector = app.control.inspect()
        active_tasks = inspector.active()
        if active_tasks:
            for key in active_tasks:
                for item in active_tasks[key]:
                    revoke(item.get("id"))

        reserved_tasks = inspector.reserved()
        if reserved_tasks:
            for key in reserved_tasks:
                for item in active_tasks[key]:
                    revoke(item.get("id"))
