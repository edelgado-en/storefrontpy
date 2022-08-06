from django.dispatch import Signal

# Here is where you created custom signals

order_created = Signal()

# If you want MULTIPLE APPS to listen to a specific signal (event), you need to import that event in that app and so something
