from django.urls import path
from . import views

app_name = 'event_calendar'

urlpatterns = [
    path('', views.calendar_view, name='event_calendar'),
    path('events/', views.get_events, name='events'),
    path('add_event/', views.add_event, name='add_event'),
    path('event_data/', views.get_event_data, name='get_event_data'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/update/', views.update_event, name='update_event'),
    path('delete_event/<slug:slug>/', views.delete_event, name='delete_event'),
]