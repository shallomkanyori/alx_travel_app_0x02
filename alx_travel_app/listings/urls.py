from rest_framework import routers
from django.urls import path, include
from .views import ListingViewSet, BookingViewSet, user_listings, user_bookings, listing_bookings, initiate_payment, verify_payment

router = routers.DefaultRouter()
router.register('listings', ListingViewSet)
router.register('bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('listings/<listing_id>/bookings/', listing_bookings),
    path('users/<user_id>/bookings/', user_bookings),
    path('users/<user_id>/listings/', user_listings),
    path('payment/initiate', initiate_payment),
    path('payment/verify/<tx_ref>', verify_payment)
]