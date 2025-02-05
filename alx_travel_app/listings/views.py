from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Listing, Booking, Review
from django.contrib.auth.models import User
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from django.conf import settings
import requests
import json
import uuid

@api_view(['POST'])
def initiate_payment(request):
    url = "https://api.chapa.co/v1/transaction/initialize"
    body = json.loads(request.body.decode('utf-8'))
    user = request.user
    transaction_reference = f"ALX_travelapp-{uuid.uuid4().hex}"

    payload = {
        "amount": body['amount'],
        "currency": "ETB",
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "tx_ref": transaction_reference,
        "callback_url": request.build_absolute_uri(f'/payment/verify/{transaction_reference}'),
        "customization": {
            "title": "ALX Travel App",
            "description": "Payment for booking a property",
        }
    }

    headers = {
        'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()

    PaymentSerializer.create({
        'booking_id': body['booking_id'],
        'amount': body['amount'],
        'payment_method': 'chapa',
        'transaction_id': transaction_reference
    })


    response_data['tx_ref'] = transaction_reference
    return Response(response_data)

@api_view(['GET'])
def verify_payment(request, tx_ref):
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    payload = ''
    headers = {
        'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'
    }

    response = requests.get(url, headers=headers, data=payload)
    response_data = response.json()

    payment = PaymentSerializer.get_by_transaction_id(tx_ref)
    payment_status = response_data['status'] === 'success' ? 'completed' : 'failed'
    serializer = PaymentSerializer(payment, data={'payment_status': payment_status}, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(response_data)

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

@api_view(['GET'])
def user_listings(request, user_id=None):
    user = (user_id or request.user.id)
    listings = Listing.objects.filter(host_id=user)
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request):
        property_id = request.data.get('property_id')
        user_id = request.data.get('user_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        total_price = request.data.get('total_price')

        property = get_object_or_404(Listing, listing_id=property_id)
        user = get_object_or_404(User, id=user_id)

        booking = Booking.objects.create(
            property_id=property,
            user_id=user,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )

        booking.save()

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])    
def user_bookings(request, user_id=None):
    user = (user_id or request.user.id)
    bookings = Booking.objects.filter(user_id=user)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def listing_bookings(request, listing_id=None):
    listing = get_object_or_404(Listing, listing_id=listing_id)
    bookings = Booking.objects.filter(property_id=listing)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)