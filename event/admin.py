from django.contrib import admin

from event.models import (
    EventCategory, 
    Event,
)

admin.site.register(EventCategory)
admin.site.register(Event)
