from django.shortcuts import render, get_object_or_404
from .models import Person

def index(request):
    return render(request, 'index.html')

def search(request):
    query = request.GET.get('q', '')
    results = Person.objects.filter(
        name__icontains=query
    ) | Person.objects.filter(
        top_skills__icontains=query
    ) | Person.objects.filter(
        other_skills__icontains=query
    )

    return render(request, 'search_results.html', {
        'query': query,
        'results': results
    })

def person_detail(request, pk):
    person = get_object_or_404(Person, pk=pk)
    return render(request, 'person_detail.html', {'person': person})
