from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.timezone import localtime


from event.models import (
    EventCategory,
    Event
)
from event.forms import (
    CreateCategoryForm,
    UpdateCategoryForm,
    CreateEventForm,
    UpdateEventForm,
)
from event.helpers import generate_repeating_events
from account.models import Account

def create_category_view(request):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')
    
    form = CreateCategoryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        ## Get and set the fields that are ForeignKey in models
        obj = form.save(commit=False)
        created_user = Account.objects.filter(email=user.email).first()
        obj.created_user = created_user
        obj.save() #Save the category post
        form = CreateCategoryForm()
        return redirect('home')
    
    context['form'] = form

    return render(request, 'event/create_category.html', context)
    

def create_event_view(request, slug):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')
    
    category = get_object_or_404(EventCategory, slug=slug)

    if request.method == "POST":
        # Изпраща формата
        form = CreateEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.category = category
            event.created_user = user
            event.save()
            if event.end_repeat_date is not None:
                generate_repeating_events(event, event.end_repeat_date)
            return redirect('event:detail-category', slug=category.slug)
    else:
        # Показва формата
        form = CreateEventForm()
    
    context['form'] = form
    return render(request, 'event/create_event.html', context)

def detail_category_view(request, slug):
    EVENTS_PER_PAGE = 3
    context = {}

    category = get_object_or_404(EventCategory, slug=slug)
    status_filter = request.GET.get('status')

    if status_filter in dict(Event.STATUS):
        event_list = Event.objects.filter(category=category, status=status_filter)
    else:
        event_list = Event.objects.filter(category=category)

    #Pagination
    page = request.GET.get('page', 1)
    event_paginator = Paginator(event_list, EVENTS_PER_PAGE)

    try:
        event_list = event_paginator.page(page)
    except PageNotAnInteger:
        event_list = event_paginator.page(EVENTS_PER_PAGE)
    except EmptyPage:
        event_list = event_paginator.page(event_paginator.num_pages)
    
    context['status_filter'] = status_filter
    context['category'] = category
    context['event_list'] = event_list

    return render(request, 'event/detail_category.html', context)

def detail_event_view(request, slug):
    context = {}

    event = get_object_or_404(Event, slug=slug)
    context['event'] = event
    category = event.category
    context['category'] = category
    participants = list([user.username for user in event.participants.all()])
    participants.append(event.created_user.username)
    participants = ', '.join(participants)
    context['participants'] = participants

    return render(request, 'event/detail_event.html', context)

def add_participant_to_event(request, slug):
    event = get_object_or_404(Event, slug=slug)

    if not request.user.is_authenticated:
        return redirect("must_authenticate")

    if request.user not in event.participants.all():
        event.participants.add(request.user)

    return redirect('event:detail-event', slug=slug)

def edit_category_view(request, slug):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')
    
    category = get_object_or_404(EventCategory, slug=slug)

    if category.created_user != user:
        return HttpResponse("You do not have perms to edit this category.")
    
    if request.POST:
        form = UpdateCategoryForm(request.POST or None, request.FILES or None, instance=category)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            context['success_message'] = "Updated"
            category = obj
    
    form = UpdateCategoryForm(
        initial= {
            "name": category.name,
            "description": category.description,
            "priority": category.priority,
            "image": category.image,
        }
    )

    context['form'] = form

    return render(request, 'event/edit_category.html', context)

def edit_event_view(request, slug):
    context = {}
    user = request.user

    if not user.is_authenticated:
        return redirect('must_authenticate')
    
    event = get_object_or_404(Event, slug=slug)
    if (event.created_user != user) and (user not in event.participants.all()):
        return HttpResponse("You do not have perms to edit this event.")
    
    if request.POST:
        form = UpdateEventForm(request.POST or None, instance=event)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            context['success_message'] = "Updated"
            event = obj
    else:
        form = UpdateEventForm(instance=event)

        form.fields['start_date'].initial = format(localtime(event.start_date), 'Y-m-d\\TH:i')
        form.fields['end_date'].initial = format(localtime(event.end_date), 'Y-m-d\\TH:i')

    context['form'] = form
    context['event'] = event
    return render(request, 'event/edit_event.html', context)


def get_category_queryset(query=None):
    queryset = []
    queries = query.split(" ") #New category -> ['New', 'category']
    for q in queries:
        category_list = EventCategory.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        ).distinct()
    
        queryset.extend(category_list)
    
    return list(set(queryset))

def delete_category_view(request, slug):
    user = request.user

    if not user.is_authenticated:
        return redirect('must_authenticate')
    
    category = get_object_or_404(EventCategory, slug=slug)
    if category.created_user != user:
        return HttpResponse("You do not have perms to delete this category.")
    
    category.delete()
    return redirect('home')

def delete_event_view(request, slug):
    user = request.user

    if not user.is_authenticated:
        return redirect('must_authenticate')
    
    event = get_object_or_404(Event, slug=slug)
    if (event.created_user != user) and (user not in event.participants.all()):
        return HttpResponse("You do not have perms to delete this event.")
    
    category = event.category
    event.delete()
    return redirect('event:detail-category', category.slug)