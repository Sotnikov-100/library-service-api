from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowings.models import Borrowing
from payments.services import create_payment_for_borrowing


@receiver(post_save, sender=Borrowing)
def create_payment_for_new_borrowing(sender, instance, created, **kwargs):
    if created:
        create_payment_for_borrowing(instance)