from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from django.utils.timezone import make_aware
from pytz import timezone

import json

from event.models import EventCategory, Event
from event.helpers import generate_repeating_events
from account.models import Account


# Защита срещу атаки
@csrf_exempt
def calendar_view(request):
    return render(request, 'event_calendar/calendar.html')

def get_events(request):
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)

    if start and end:
        events = Event.objects.filter(
            Q(start_date__gte=datetime.fromisoformat(start), end_date__lte=datetime.fromisoformat(end)),
            Q(created_user=request.user) | Q(participants=request.user)).distinct()
    else:
        events = Event.objects.filter(
            Q(created_user=request.user) | Q(participants=request.user)
        ).distinct()
    
    event_list = []
    for event in events:
        event_list.append({
            "id": event.id,
            "title": event.name,
            "start": event.start_date.isoformat(),
            "end": event.end_date.isoformat(),
            "description": event.description,
            "status": event.status,
            "repeat": event.repeat,
            "slug": event.slug,
            "category": event.category.name,
            "backgroundColor": "#ffc107" if event.status == "future" else "#28a745",
            "borderColor": "#000000",
        })
    
    return JsonResponse(event_list, safe=False)

def all_events(request):
    event_list = Event.objects.filter(
        Q(created_user=request.user) | Q(participants=request.user)
    ).distinct()
    out = []

    for event in event_list:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start_date,
            'end': event.end_date,
        })

    return JsonResponse(out, safe=False)

def add_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Задай времевата зона за България
            sofia_tz = timezone('Europe/Sofia')

            # Чета датите от заявката
            start_date = datetime.fromisoformat(data['start'])
            end_date = datetime.fromisoformat(data['end'])
            end_repeat_date = data.get('end_repeat_date')
            if end_repeat_date:
                end_repeat_date = datetime.strptime(end_repeat_date, '%Y-%m-%d').date()

            # Конвертирам към timezone-aware дати
            if not start_date.tzinfo:
                start_date = make_aware(start_date, sofia_tz)
            if not end_date.tzinfo:
                end_date = make_aware(end_date, sofia_tz)

            event = Event(
                name=data['title'],
                description=data['description'],
                status=data['status'],
                start_date=start_date,
                end_date=end_date,
                repeat=data['repeat'],
                end_repeat_date=end_repeat_date,
                category_id=data['category'],
                created_user=request.user
            )

            event.save()
            event.participants.set(data.get('participants', []))

            if event.repeat != 'none' and event.end_repeat_date:
                generate_repeating_events(event, event.end_repeat_date)
            
            return JsonResponse({'message': 'Event added successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest("Invalid request method")
        
@login_required
@csrf_exempt
def update_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            event.name = data.get('title', event.name)
            event.description = data.get('description', event.description)
            event.status = data.get('status', event.status)
            event.start_date = datetime.fromisoformat(data.get('start', event.start_date.isoformat()))
            event.end_date = datetime.fromisoformat(data.get('end', event.end_date.isoformat()))
            event.category_id = data.get('category', event.category_id)
            event.participants.set(data.get('participants', event.participants.all()))
            event.save()
            return JsonResponse({'message': 'Event updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
@login_required
@csrf_exempt
def delete_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'DELETE':
        event.delete()
        return JsonResponse({'message': 'Event deleted successfully'})

@login_required
def get_event_data(request):
    categories = EventCategory.objects.filter(created_user=request.user)
    users = Account.objects.exclude(id=request.user.id)

    category_list = [{"id": c.id, "name": c.name} for c in categories]
    user_list = [{"id": user.id, "username": user.username} for user in users]

    return JsonResponse({"categories": category_list, "users": user_list})

@login_required
def event_detail(request, slug):
    try:
        event = get_object_or_404(Event, slug=slug)
        participants = list([user.username for user in event.participants.all()])
        participants.append(event.created_user.username)
        event_data = {
            'name': event.name,
            'description': event.description,
            'status': event.status,
            'start_date': event.start_date.isoformat(),
            'end_date': event.end_date.isoformat(),
            'repeat': event.repeat,
            'category': event.category.name,
            'created_user': event.created_user.username,
            'participants': participants
        }
        return JsonResponse(event_data)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

