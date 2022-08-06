# Signals allows us to decouple our apps using pre_save (fire before a model is saved) and post_save (fire after a model is saved)
# pre_delete (fire before a model is deleted) and post_delete (fire after a model is deleted)
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Customer

# we specify a sender because we don't want to fire this signal for every post_save for all models
# we use settings.AUTH_USER_MODEL instead of directly accessing the User model to avoid adding a dependency of the Core app in the Store app.

# BUT THIS CODE IS NOT USED UNLESS WE IMPORTED SOMEWHERE. We have to imported in the apps.py file of this app

# every model in django fires signals (kinda like triggers in SQL), I can create my own custom signals as well


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    """
    This is called a signal handler
    """
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])
