from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from django.utils import timezone

from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from account.tasks import annual_recap_task
from event.models import EventCategory, Event
from event.helpers import generate_upcoming_events

def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=password)
            login(request, account)
            return redirect('home')
        else:
            context['registration_form'] = form
    else: #request.GET
        form = RegistrationForm()
        context['registration_form'] = form
    
    return render(request, 'account/register.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request):
    context = {}
    user = request.user

    if user.is_authenticated:
        return redirect('home')
    
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AccountAuthenticationForm()
    
    context['login_form'] = form
    return render(request, 'account/login.html', context)
    
def account_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.initial = {
                "email": request.POST['email'],
                "username": request.POST['username'],
            }
            form.save()
            context['success_msg'] = "Updated"
    else:
        form = AccountUpdateForm(
            initial={ #Какво да се визуализира при достъпване на профила, преди да се опитат да ги променят
                "email": request.user.email,
                "username": request.user.username,
            }
        )
    
    context['account_form'] = form

    categories = EventCategory.objects.filter(created_user=request.user)
    context['category_list'] = categories
    upcoming_events = generate_upcoming_events(request.user)
    event_list = Event.objects.filter(
        Q(created_user=request.user) | Q(participants=request.user)
    ).distinct()

    context['upcoming_events'] = upcoming_events
    context['event_list'] = event_list
    
    today = timezone.now().date()
    recap_data = None
    
    #За тестване махам проверката за месец и ден
    if not recap_data and today.month == 12 and today.day == 31:
        recap_data = annual_recap_task(request.user)
    
    context['recap_data'] = recap_data
    
    return render(request, 'account/account.html', context)

def must_authenticate_view(request):
    return render(request, 'account/must_authenticate.html', {})