from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Person, Skill

def index(request):
    return render(request, 'index.html')

def search(request):
    query = request.GET.get('q', '')
    title_filter = request.GET.get('title', '')
    division_filter = request.GET.get('division', '')
    program_filter = request.GET.get('program', '')

    results = Person.objects.all()

    if query:
        results = results.filter(
            name__icontains=query
        ) | results.filter(
            top_skills__icontains=query
        ) | results.filter(
            other_skills__icontains=query
        )

    if title_filter:
        results = results.filter(title=title_filter)

    if division_filter and division_filter != 'All':
        results = results.filter(division=division_filter)

    if program_filter:
        results = results.filter(program=program_filter)

    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
        'title_filter': title_filter,
        'division_filter': division_filter,
        'program_filter': program_filter
    })

def person_detail(request, name, unique_id_part):
    person = get_object_or_404(Person, name=name, unique_id__startswith=unique_id_part)
    # return render(request, 'person_detail.html', {'person': person})
    top_skills_list = [skill.strip() for skill in person.top_skills.split(',')] if person.top_skills else []

    return render(request, 'person_detail.html', {
        'person': person,
        'top_skills_list': top_skills_list
    })


def get_graph_data(request):
    person_name = request.GET.get('person', None)

    nodes = []
    edges = []
    skill_set = set()
    name_to_skills = {}
    name_to_info = {}
    name_to_unique_id = {}

    people = Person.objects.all()

    for person in people:
        name = person.name
        unique_id = person.unique_id
        top_skills = [skill.strip() for skill in person.top_skills.split(',')][:5]
        name_to_skills[name] = top_skills
        name_to_info[name] = {
            'Title': person.title or 'N/A',
            'Division': person.division or 'N/A',
            'Program': person.program or 'N/A',
            'Bio': person.bio or 'N/A',
            'Email': person.email or 'N/A',
            'Other Skills': person.other_skills or 'N/A'
        }
        name_to_unique_id[name] = unique_id
        skill_set.update(top_skills)

    if person_name:
        person_name = person_name.strip()
        if person_name in name_to_skills:
            top_skills = name_to_skills[person_name]
            unique_id = name_to_unique_id.get(person_name, '')
            nodes.append({
                'id': unique_id,
                'label': person_name,
                'group': 'name',
                'title': f"Title: {name_to_info[person_name]['Title']}<br>"
                         f"Division: {name_to_info[person_name]['Division']}<br>"
                         f"Program: {name_to_info[person_name]['Program']}<br>"
                         f"Bio: {name_to_info[person_name]['Bio']}<br>"
                         f"Email: {name_to_info[person_name]['Email']}<br>"
                         f"Other Skills: {name_to_info[person_name]['Other Skills']}"
            })
            for skill in top_skills:
                nodes.append({
                    'id': skill,
                    'label': skill,
                    'group': 'skill'
                })
                edges.append({
                    'from': unique_id,
                    'to': skill
                })

            for skill in top_skills:
                for other_name, other_skills in name_to_skills.items():
                    if other_name != person_name and skill in other_skills:
                        other_unique_id = name_to_unique_id.get(other_name, '')
                        nodes.append({
                            'id': other_unique_id,
                            'label': other_name,
                            'group': 'name',
                            'title': f"Title: {name_to_info[other_name]['Title']}<br>"
                                     f"Division: {name_to_info[other_name]['Division']}<br>"
                                     f"Program: {name_to_info[other_name]['Program']}<br>"
                                     f"Bio: {name_to_info[other_name]['Bio']}<br>"
                                     f"Email: {name_to_info[other_name]['Email']}<br>"
                                     f"Other Skills: {name_to_info[other_name]['Other Skills']}"
                        })
                        edges.append({
                            'from': other_unique_id,
                            'to': skill
                        })

    return JsonResponse({'nodes': nodes, 'edges': edges})

from django.conf import settings
def passcode_check(request):
    if request.method == 'POST':
        entered_passcode = request.POST.get('passcode')
        if entered_passcode == settings.PASSCODE:
            request.session['passcode_verified'] = True
            return redirect('upload_resume')
        else:
            return render(request, 'passcode_check.html', {'error': 'Invalid passcode'})
    return render(request, 'passcode_check.html')

import io
from django.views.decorators.csrf import csrf_exempt
from people.utils import *

def upload_resume(request):
    if not request.session.get('passcode_verified', False):
        return redirect('passcode_check')
    return render(request, 'upload_resume.html')

def edit_file(request, file_index):
    file_details = request.session.get('file_details', [])
    results_details = request.session.get('results', [])
    print(f"EDIT FILE: {file_details}")
    print(f"EDIT FILE Result: {results_details}")
    if file_index < 0 or file_index >= len(file_details):
        return render(request, 'edit_file.html', {'error': 'Invalid file index'})

    file_detail = file_details[file_index]
    print(file_index)
    if file_index < len(results_details):
        file_name = results_details[file_index]['filename']
    else:
        file_name = 'Unknown File'
    context = {
        'file_name': file_name,
        'file_detail': file_detail,
        'file_index': file_index,
        'file_count': len(file_details)
    }
    return render(request, 'edit_file.html', context)


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file part'})

        files = request.FILES.getlist('file')
        if not files:
            return JsonResponse({'error': 'No files selected'})

        results = []
        file_details = []

        for file in files:
            if file.content_type != 'application/pdf':
                results.append({'filename': file.name, 'status': 'error', 'error': 'File type not allowed'})
                continue

            file_content = file.read()
            pdf_file = io.BytesIO(file_content)
            client_id = "ip9yko1op2a386go"
            client_secret = "VvVpcySC"

            try:
                data = process_resume(pdf_file, client_id, client_secret)
                results.append({'filename': file.name, 'status': 'success'})
                file_details.append(data)
            except Exception as e:
                results.append({'filename': file.name, 'status': 'error', 'error': str(e)})
                file_details.append({})

        request.session['file_details'] = file_details
        request.session['results'] = results
        print(request.session['file_details'])
        print(request.session['results'])
        return JsonResponse({'results': results, 'file_details': file_details})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def process_resume(pdf_file, client_id, client_secret):
    resume_text = extract_text_from_pdf(pdf_file)
    preprocessed_text = preprocess_text(resume_text)
    tokens = tokenize_and_process(preprocessed_text)

    access_token = get_lightcast_access_token(client_id, client_secret)
    specialized_skills = extract_lightcast_skills(access_token, resume_text)

    name, email = extract_personal_info(resume_text)

    return {
        "name": name,
        "email": email,
        "topSkills": specialized_skills[:5],
        "otherSkills": specialized_skills[5:]
    }


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def save_to_database(name, email, title, division, program, bio, top_skills, other_skills, unique_id):
    person, created = Person.objects.update_or_create(
        unique_id=unique_id,
        defaults={
            'name': name,
            'email': email,
            'title': title,
            'division': division,
            'program': program,
            'bio': bio,
            'top_skills': ', '.join(top_skills),
            'other_skills': ', '.join(other_skills)
        }
    )
    if created:
        print(f"New entry created: {unique_id}")
    else:
        print(f"Existing entry updated: {unique_id}")

from django.urls import reverse
@csrf_exempt
def save_details(request):
    if request.method == 'POST':
        print("Request POST data:", request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        title = request.POST.get('title')
        division = request.POST.get('division')
        program = request.POST.get('program')
        bio = request.POST.get('bio')
        unique_id = request.POST.get('id')
        top_skills = [skill.strip() for skill in (request.POST.get('top_skills', '')).split(',') if skill.strip()]
        other_skills = [skill.strip() for skill in (request.POST.get('other_skills', '')).split(',') if skill.strip()]

        try:
            print(f"Saving details with unique_id: {unique_id}")
            save_to_database(name, email, title, division, program, bio, top_skills, other_skills, unique_id)
            file_index = int(request.POST.get('file_index', 0))
            file_details = request.session.get('file_details', [])
            file_count = len(file_details)
            next_file_index = file_index + 1
            if next_file_index < file_count:
                return JsonResponse({
                    'message': 'Details saved successfully',
                    'next_url': f"{reverse('edit_file', kwargs={'file_index': next_file_index})}"
                })
            else:
                return JsonResponse({'message': 'Details saved successfully', 'next_url': reverse('upload_resume')})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method'})

import uuid
@csrf_exempt
def save_file_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file_details = request.session.get('file_details', [])

        results_details = data.get('results', [])
        new_file_details = data.get('file_details', [])

        file_details_map = {file_detail['id']: file_detail for file_detail in file_details if 'id' in file_detail}
        for file_detail in new_file_details:
            file_id = file_detail.get('id')
            if not file_id:
                file_id = str(uuid.uuid4())
                file_detail['id'] = file_id
            file_details_map[file_id] = file_detail
        file_details = list(file_details_map.values())

        results_map = {result['filename']: result for result in results_details}
        for result in results_details:
            results_map[result['filename']] = result
        results_details = list(results_map.values())

        request.session['file_details'] = file_details
        request.session['results'] = results_details
        return JsonResponse({'message': 'File details saved'})
    else:
        return JsonResponse({'error': 'Invalid request method'})
def skill_suggestions(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__icontains=q).values_list('name', flat=True)
    return JsonResponse({'suggestions': list(skills)})

def edit_person(request, unique_id):
    person = get_object_or_404(Person, unique_id=unique_id)

    if request.method == 'POST':
        top_skills = request.POST.get('top_skills', '')
        other_skills = request.POST.get('other_skills', '')

        # Split and clean the skills (remove whitespace, etc.)
        top_skills_list = [skill.strip() for skill in top_skills.split(',') if skill.strip()]
        other_skills_list = [skill.strip() for skill in other_skills.split(',') if skill.strip()]

        # Get valid skills from the database
        valid_skills = set(Skill.objects.values_list('name', flat=True))

        # # Add invalid skills to the database
        # all_skills = top_skills_list + other_skills_list
        # for skill in all_skills:
        #     if skill not in valid_skills:
        #         Skill.objects.get_or_create(name=skill)
        #         valid_skills.add(skill)

        if (skill in valid_skills for skill in top_skills_list + other_skills_list):
            person.name = request.POST.get('name')
            person.title = request.POST.get('title')
            person.division = request.POST.get('division')
            person.program = request.POST.get('program')
            person.email = request.POST.get('email')
            person.bio = request.POST.get('bio')
            person.top_skills = ','.join(top_skills_list)
            person.other_skills = ','.join(other_skills_list)
            person.save()
            return redirect('person_detail', name=person.name, unique_id_part=person.unique_id)
        else:
            return render(request, 'edit_person.html', {
                'person': person,
                'error': 'Invalid skills provided.',
                'top_skills': top_skills_list,
                'other_skills': other_skills_list,
            })

    top_skills = person.top_skills.split(',') if person.top_skills else []
    other_skills = person.other_skills.split(',') if person.other_skills else []

    return render(request, 'edit_person.html', {
        'person': person,
        'top_skills': top_skills,
        'other_skills': other_skills,
    })