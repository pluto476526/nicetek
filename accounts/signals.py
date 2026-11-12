from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import User


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Handle user post-save"""
    if created and instance.role == "client":
        # Auto-create Client profile for client users
        def create_client():
            from clients.models import Client
            Client.objects.get_or_create(
                user=instance,
                defaults={
                    'company_name': instance.company or instance.get_full_name(),
                    'phone': instance.phone or '+254000000000',
                    'address': 'To be updated',
                    'town': 'Nairobi',
                    'county': 'Nairobi',
                }
            )
        
        transaction.on_commit(create_client)