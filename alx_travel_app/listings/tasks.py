from celery import shared_task
from models import Payment
from django.contrib.auth.models import User
from django.core.mail import send_mail

@shared_task
def send_payment_email(transaction_id):
    payment = Payment.objects.get(transaction_id=transaction_id)
    user = User.objects.get(id=payment.booking_id.user_id)
    send_mail(
        'Payment Confirmation',
        f'Your payment of {payment.amount} ETB has been received.',
        None,
        [user.email],
        fail_silently=False,
    )