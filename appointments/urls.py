from rest_framework import routers

from .views import AppointmentView

router = routers.SimpleRouter()

app_name = "booking"

router.register(r"booking", AppointmentView, basename="Booking")

urlpatterns = []
urlpatterns += router.urls
