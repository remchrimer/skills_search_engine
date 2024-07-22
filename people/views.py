from django.shortcuts import render
from .models import Person

def index(request):
    return render(request, 'index.html')

def search(request):
    query = request.GET.get('q')
    if query:
        results = Person.objects.filter(
            name__icontains=query
        ) | Person.objects.filter(
            top_skills__icontains=query
        ) | Person.objects.filter(
            other_skills__icontains=query
        )
    else:
        results = Person.objects.none()
    return render(request, 'search_results.html', {'results': results, 'query': query})
