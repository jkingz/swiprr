import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import decorators, generics, mixins, response, status, viewsets
from rest_framework.permissions import IsAuthenticated

from .constants import (
    EmailType,
    ClientMessages,
    AgentMessages,
    AdminMessages,
)

from .utils import (
    _send_client_notification,
    _send_agent_notification,
    _send_admin_notification,
)

from users.models import User

from .models import Booking, BookingClient
from .serializers import BookingSerializer


# Create your views here.
class AppointmentView(viewsets.ModelViewSet, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def list(self, request, **kwargs):
        # List of all possible query parameters
        queryset = self.get_queryset()
        user_id = self.request.query_params.get("user_id", None)
        date = self.request.query_params.get("date", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        booking_id = self.request.query_params.get("booking_id", None)
        property_id = self.request.query_params.get("property_id", None)
        gte_this_date = self.request.query_params.get("gte_this_date", None)
        lt_this_date = self.request.query_params.get("lt_this_date", None)

        # Remove this after the api is migrated to new version in the frontend.
        if (
            user_id
            and not start_date
            and not end_date
            and not date
            and not property_id
            and not gte_this_date
            and not lt_this_date
        ):
            user_bookings = queryset.filter(booking_client__user__id=int(user_id))
            return response.Response(
                self.get_serializer(user_bookings, many=True).data,
                status=status.HTTP_200_OK,
            )
        # Return bookings on date specified
        elif date and not user_id:
            bookings = queryset.filter(booking_date=date)
            return response.Response(
                self.get_serializer(bookings, many=True).data, status=status.HTTP_200_OK
            )
        # Return bookings on date range specified
        elif start_date and end_date and not user_id:
            bookings = queryset.filter(booking_date__range=[start_date, end_date])
            return response.Response(
                self.get_serializer(bookings, many=True).data, status=status.HTTP_200_OK
            )
        # Return bookings on date range specified for a specific user
        elif start_date and end_date and user_id:
            bookings = queryset.filter(
                booking_date__range=[start_date, end_date], booking_client__user__id=user_id
            )
            return response.Response(
                self.get_serializer(bookings, many=True).data, status=status.HTTP_200_OK
            )
        # Return bookings on specified user and booking
        elif user_id and booking_id:
            bookings = queryset.filter(
                booking_date__range=[start_date, end_date], booking_client__user__id=user_id
            )
            return response.Response(
                self.get_serializer(bookings, many=True).data, status=status.HTTP_200_OK
            )
        # Return bookings on specified user and property
        elif user_id and property_id:
            bookings = queryset.filter(
                booking_client__user__id=int(user_id), booked_property__id=int(property_id)
            )
            return response.Response(
                self.get_serializer(bookings, many=True).data, status=status.HTTP_200_OK
            )
        # Return bookings of the user that is greater than or equal to the time given
        elif gte_this_date and user_id:
            gte_this_date = datetime.datetime.strptime(gte_this_date, '%Y-%m-%d').date()
            date = datetime.timedelta(days=7)

            selected_date = gte_this_date - date
            if self.request.user.is_superuser:
                bookings = queryset.filter(
                    booking_date__gte=selected_date
                ).order_by('-booking_date')
            else:
                bookings = queryset.filter(
                    booking_date__gte=selected_date, booking_client__user__id=int(user_id)
                ).order_by('-booking_date')
            return response.Response(
                self.get_serializer(bookings, many=True).data, status=status.HTTP_200_OK
            )
        elif lt_this_date and user_id:
            if self.request.user.is_superuser:
                bookings = queryset.filter(
                    booking_date__lt=lt_this_date
                )
            else:
                bookings = queryset.filter(
                    booking_date__lt=lt_this_date, booking_client__user__id=int(user_id)
                )
            return response.Response(
                self.get_serializer(bookings, many=True).data, status=status.HTTP_200_OK
            )

        data = self.get_serializer(queryset, many=True).data
        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["get"], name="All Agent's Booking Assigned")
    def agent_booking(self):
        queryset = self.get_queryset()
        agent_assigned_booking = queryset.filter(agents__id=self.request.query_params.get('user_id'))
        data = self.get_serializer(agent_assigned_booking, many=True).data

        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["get"], name="All Users Bookings")
    def users_booking(self, pk=None):
        queryset = self.get_queryset()
        user_bookings = queryset.filter(booking_client__user__id=int(pk))
        data = self.get_serializer(user_bookings, many=True).data

        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], name="Cancel Booking")
    def cancel_booking(self, request, pk=None):
        approved_by = request.data.get("approved_by", None)
        date_canceled = request.data.get("date_canceled", None)
        cancel_reason = request.data.get("cancel_reason", None)
        user = User.objects.get(pk=int(approved_by))
        queryset = self.get_queryset()
        if not date_canceled:
            return response.Response(
                {"detail": "date_canceled value is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            to_cancel_booking = queryset.get(id=int(pk))
            to_cancel_booking.is_approved = False
            to_cancel_booking.date_canceled = date_canceled
            to_cancel_booking.is_pending = False
            to_cancel_booking.approved_by = user
            to_cancel_booking.cancel_reason = cancel_reason
            to_cancel_booking.save()

        except Booking.DoesNotExist:
            return response.Response(
                {"detail": "Booking does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_serializer(to_cancel_booking).data

        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], name="Approve Booking")
    def approve_booking(self, request, pk=None):

        approved_by = request.data.get("approved_by", None)
        user = User.objects.get(pk=int(approved_by))
        queryset = self.get_queryset()
        if not approved_by:
            return response.Response(
                {"detail": "approved_by value is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            to_approve_booking = queryset.get(id=int(pk))
            to_approve_booking.is_pending = False
            to_approve_booking.is_approved = True
            to_approve_booking.date_canceled = None
            to_approve_booking.approved_by = user
            to_approve_booking.save()

        except Booking.DoesNotExist:
            return response.Response(
                {"detail": "Booking does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_serializer(to_approve_booking).data

        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], name="Assign booking")
    def assign_booking(self, request, pk=None):
        agents = request.data.get("agents", None)
        queryset = self.get_queryset()
        try:
            booking = queryset.get(pk=int(pk))
            for agent in agents:
                user = get_user_model().objects.get(email=agent)
                booking.agents.add(user)
            # list of agents to be removed.
            to_remove = booking.agents.exclude(email__in=agents)
            if to_remove:
                for agent in to_remove:
                    booking.agents.remove(agent)
        except Booking.DoesNotExist:
            return response.Response(
                {"detail": "Assigned to value is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_serializer(booking).data
        _send_agent_notification(booking, EmailType.AGENT_ASSIGNMENT,
                                 AgentMessages.AGENT_ASSIGNMENT_ALL_MESSAGE, agents)
        _send_admin_notification(booking, EmailType.AGENT_ASSIGNMENT,
                                 AdminMessages.AGENT_ASSIGNMENT_MESSAGE)

        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], name="Assign booking client")
    def assign_clients(self, request, pk=None):
        clients = request.data.get("clients", None)
        queryset = self.get_queryset()
        try:
            booking = queryset.get(pk=int(pk))
            users = get_user_model().objects.filter(email__in=clients)
            for client in users:
                BookingClient.objects.get_or_create(
                    user=client,
                    email=client.email,
                    first_name=client.first_name,
                    last_name=client.last_name,
                    booking=booking
                )
            # list of clients to be removed.
            to_remove = booking.booking_client.exclude(email__in=clients)
            if to_remove:
                to_remove.delete()

        except Booking.DoesNotExist:
            return response.Response(
                {"detail": "Assigned to value is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_serializer(booking).data

        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["get"], name="Get Assigned Booking")
    def get_assigned_booking(self, pk=None):
        queryset = self.get_queryset()
        get_assigned_booking = queryset.filter(assigned_to=int(pk))
        data = self.get_serializer(get_assigned_booking, many=True).data

        return response.Response(data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], name="Unlock Booking")
    def unlock_booking(self, request, pk=None):
        queryset = self.get_queryset()
        to_unlock_booking = queryset.filter(id=int(pk))
        to_unlock_booking.update(
            is_pending=True, is_approved=False, approved_by=None, date_canceled=None
        )
        data = self.get_serializer(to_unlock_booking, many=True).data
        # Commenting this out for now since the reschedule feature is not yet built.
        # _send_client_notification(to_unlock_booking[0], EmailType.UNLOCKED_BOOKING,
        #                           ClientMessages.UNLOCKED_BOOKING_MESSAGE)

        return response.Response(data, status=status.HTTP_200_OK)
