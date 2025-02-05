from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
    
    def get_by_transaction_id(self, transaction_id):
        return Payment.objects.get(transaction_id=transaction_id)