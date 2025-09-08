from django.contrib import admin
from .models import *

admin.site.register(Service)
admin.site.register(Place)
admin.site.register(TimeSlot)
admin.site.register(Reservation)
admin.site.register(Customer)
