from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Event
from datetime import timedelta
import pytz

@shared_task(name='event_notifications')
def send_event_notifications():
    current_timezone = pytz.timezone('Europe/Sofia')

    now = timezone.now().astimezone(current_timezone)
    upcoming_events = Event.objects.filter(
        start_date__gt=now,
        start_date__lt=now + timedelta(days=1)  # Само събития в следващите 24 часа
    )


    for event in upcoming_events:
        subject = f"pyCalendar"
        body = render_to_string('event/snippets/email_notification.html', {'user': event.created_user.username,
                                                                           'weekday': event.start_date.strftime('%A'),
                                                                           'date': event.start_date,
                                                                           'hour': event.start_date,
                                                                           'event': event.name})
        
        
        msg = EmailMessage(subject, body, to=[event.created_user.email])
        msg.content_subtype = 'html'
        msg.send()

        for participant in event.participants.all():
            body = render_to_string('event/snippets/email_notification.html', {'user': participant.username,
                                                                           'weekday': event.start_date.strftime('%A'),
                                                                           'date': event.start_date,
                                                                           'hour': event.start_date,
                                                                           'event': event.name})
        
            msg = EmailMessage(subject, body, to=[participant.email])
            msg.content_subtype = 'html'
            msg.send()
