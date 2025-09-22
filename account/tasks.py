from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from event.models import Event

@shared_task(name='recap')
def annual_recap_task(user=None):
    target_year = timezone.now().year
    
    # Филтриране на събития за целевата година
    events = Event.objects.filter(
        Q(created_user=user) | Q(participants=user)
    ).distinct()
    
    # Изчисляване на статистиките
    total_events = events.count()
    
    status_counts = {
        'active': events.filter(status='active').count(),
        'future': events.filter(status='future').count(),
        'past': events.filter(status='past').count()
    }
    
    # Пресмятане на общо време
    total_duration = timedelta()
    for event in events:
        duration = event.end_date - event.start_date
        total_duration += duration
    
    # Конвертиране на времето в дни и часове
    total_days = total_duration.days
    total_hours = total_duration.seconds // 3600
    
    # Подготовка на резултата
    recap = {
        'year': target_year,
        'total_events': total_events,
        'status_distribution': status_counts,
        'total_time': {
            'days': total_days,
            'hours': total_hours
        }
    }
    
    return recap