from core.utils import HomeswiprMailer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Booking, BookingClient


class CreateBookingClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookingClient
        fields = ("first_name", "last_name", "email", "phone_number", "user")


class BookingSerializer(serializers.ModelSerializer):
    booking_client = CreateBookingClientSerializer(many=True)
    approved_by = serializers.SerializerMethodField()
    property_tz = serializers.SerializerMethodField()
    property_is_active = serializers.SerializerMethodField()
    property_name = serializers.CharField(
        source="booked_property.related_address", read_only=True
    )
    listing_id = serializers.CharField(
        source="booked_property.listing_id", read_only=True
    )

    class Meta:
        model = Booking
        fields = (
            "id",
            "agents",
            "booked_property",
            "booking_client",
            "booking_date",
            "booking_time",
            "property_name",
            "date_canceled",
            "date_created",
            "is_approved",
            "approved_by",
            "listing_id",
            "is_pending",
            "property_tz",
            "cancel_reason",
            "property_is_active"
        )

    def create(self, validated_data):
        clients = validated_data.pop('booking_client')
        instance = Booking.objects.create(
            booked_property=validated_data.get('booked_property'),
            booking_date=validated_data.get('booking_date'),
            booking_time=validated_data.get('booking_time')
        )

        for client in clients:
            user = client.get('user')
            BookingClient.objects.create(
                booking=instance,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone_number=user.phone_number,
                user=user
            )

        return instance

    def update(self, instance, validated_data):
        clients = validated_data.pop('booking_client')
        instance.booking_time = validated_data.get('booking_time', instance.booking_time)
        instance.booking_date = validated_data.get('booking_date', instance.booking_date)
        instance.is_approved = False
        instance.is_pending = True
        instance.save()

        return instance

    def get_property_is_active(self, obj):
        return obj.booked_property.is_active

    def get_approved_by(self, obj):
        try:
            if obj.approved_by and (
                obj.approved_by.first_name and obj.approved_by.last_name
            ):

                return "{0} {1}".format(
                    obj.approved_by.first_name, obj.approved_by.last_name
                )

            return obj.approved_by.email
        except:
            return "-"

    def get_property_tz(self, obj):
        try:
            return obj.property_tz
        except:
            return "-"

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(BookingSerializer, self).to_representation(instance)
        agents = instance.agents.all()
        if agents:
            user = get_user_model().objects.filter(pk__in=agents).values('first_name', 'last_name', 'id', 'email')
            agents_list = list()
            for agent in user:
                agents_list.append({
                    'pk': agent.get('id'),
                    'name': f"{agent.get('first_name')} {agent.get('last_name')}",
                    'email': agent.get('email')
                })
            data.update({'agents': agents_list})

        return data
