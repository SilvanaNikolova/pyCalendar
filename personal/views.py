from django.shortcuts import render
from account.models import Account
# from personal.models import Question

# Create your views here.
def home_screen_view(request):
    context = {}
    # questions = Question.objects.all()
    # context["questions"] = questions

    accounts = Account.objects.all()
    context['accounts'] = accounts

    return render(request, "personal/home.html", context)