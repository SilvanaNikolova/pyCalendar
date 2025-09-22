from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from operator import attrgetter
from event.views import get_category_queryset

CATEGORY_PER_PAGE = 3

def home_screen_view(request):
    context = {}

    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)
    
    category_list = sorted(get_category_queryset(query), key=attrgetter('updated_date'), reverse=True)

    #Pagination
    page = request.GET.get('page', 1)
    category_paginator = Paginator(category_list, CATEGORY_PER_PAGE)

    try:
        category_list = category_paginator.page(page)
    except PageNotAnInteger:
        category_list = category_paginator.page(CATEGORY_PER_PAGE)
    except EmptyPage:
        category_list = category_paginator.page(category_paginator.num_pages)
    
    context['category_list'] = category_list

    return render(request, "personal/home.html", context)