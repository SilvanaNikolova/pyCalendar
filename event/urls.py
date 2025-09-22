from django.urls import path
from event.views import (
    create_category_view,
    create_event_view,
    detail_category_view,
    detail_event_view,
    edit_category_view,
    edit_event_view,
    delete_category_view,
    delete_event_view,
    add_participant_to_event,
)

app_name = 'event'

urlpatterns = [
    path('create/', create_category_view, name='create-category'),
    path('<slug>/create-event/', create_event_view, name='create-event'),
    path('<slug>/', detail_category_view, name='detail-category'),
    path('<slug>/detail/', detail_event_view, name='detail-event'),
    path('<slug>/edit/', edit_category_view, name='edit-category'),
    path('<slug>/event-edit/', edit_event_view, name='edit-event'),
    path('<slug>/delete/', delete_category_view, name='delete-category'),
    path('<slug>/event-delete/', delete_event_view, name='delete-event'),
    path('<slug>/add-participant/', add_participant_to_event, name='add-participant'),
]