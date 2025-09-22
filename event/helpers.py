from event.models import Event
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.utils import timezone

def generate_repeating_events(event, end_repeat_date):
    start_date = event.start_date.date()

    if end_repeat_date < start_date:
        raise ValueError("End repeat date must be after the event start date.")
    
    repeat = event.repeat

    if repeat == 'none':
        return
    
    current_date = start_date
    while current_date <= end_repeat_date:
        if current_date > start_date:
            new_participants = event.participants.all()
            new_event = Event.objects.create(
                category = event.category,
                name = event.name,
                description = event.description,
                status = event.status,
                start_date = current_date,
                end_date = current_date + (event.end_date - event.start_date),
                repeat = 'none',
                created_user = event.created_user,
                slug = f"{event.slug}-{current_date.strftime('%Y%m%d')}"
            )
            new_event.participants.set(new_participants)
        
        if repeat == 'daily':
            current_date += timedelta(days=1)
        elif repeat == 'weekly':
            current_date += timedelta(weeks=1)
        elif repeat == 'monthly':
            current_date += relativedelta(months=1)
        elif repeat == 'yearly':
            current_date += relativedelta(years=1)

def generate_upcoming_events(user):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        Q(created_user=user) | Q(participants=user),
        start_date__lte=now + timedelta(hours=24),
        start_date__gte=now
    ).distinct()

    return upcoming_events
