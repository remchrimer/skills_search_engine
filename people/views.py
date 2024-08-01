from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Person
import csv

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
    return render(request, 'person_detail.html', {'person': person})


def get_graph_data(request):
    person_name = request.GET.get('person', None)
    CSV_FILE_PATH = 'data/people.csv'

    nodes = []
    edges = []
    skill_set = set()
    name_to_skills = {}
    name_to_info = {}
    name_to_unique_id = {}

    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['Name']
            unique_id = row['unique_id']
            top_skills = [skill.strip() for skill in row['Top Skills'].split(',')][:5]
            name_to_skills[name] = top_skills
            name_to_info[name] = {
                'Title': row.get('Title', 'N/A'),
                'Division': row.get('Division', 'N/A'),
                'Program': row.get('Program', 'N/A'),
                'Bio': row.get('Bio', 'N/A'),
                'Email': row.get('Email', 'N/A'),
                'Other Skills': row.get('Other Skills', 'N/A')
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

def graph_view(request):
    return render(request, 'graph.html')

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
    print(f"EDIT FILE: {file_details}")

    if file_index < 0 or file_index >= len(file_details):
        return render(request, 'edit_file.html', {'error': 'Invalid file index'})

    file_detail = file_details[file_index]
    print(len(file_details))
    context = {
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

        request.session['file_details'] = file_details
        print(results)
        print(file_details)
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

def save_to_csv(name, email, title, division, program, bio, top_skills, other_skills, unique_id):
    with open('data/people.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        print(f"final: {unique_id}")
        writer.writerow([unique_id, name, email, title, division, program, bio, ", ".join(top_skills), ", ".join(other_skills)])

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

        # Use empty strings as default values if the fields are not provided
        top_skills = [skill.strip() for skill in (request.POST.get('top_skills', '')).split(',') if skill.strip()]
        other_skills = [skill.strip() for skill in (request.POST.get('other_skills', '')).split(',') if skill.strip()]

        try:
            print(f"Saving details with unique_id: {unique_id}")
            save_to_csv(name, email, title, division, program, bio, top_skills, other_skills, unique_id)

            # Get the current file index and total file count
            file_index = int(request.POST.get('file_index', 0))
            file_details = request.session.get('file_details', [])
            file_count = len(file_details)
            # Determine the next file index
            next_file_index = file_index + 1

            if next_file_index < file_count:
                # There are more files to edit
                return JsonResponse({
                    'message': 'Details saved successfully',
                    'next_url': f"{reverse('edit_file', kwargs={'file_index': next_file_index})}"
                })
            else:
                # No more files, redirect to upload page
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
        new_file_details = data.get('file_details', [])

        # Create a map of existing file details by ID
        file_details_map = {file_detail['id']: file_detail for file_detail in file_details if 'id' in file_detail}

        # Update existing file details or add new file details
        for file_detail in new_file_details:
            file_id = file_detail.get('id')
            if not file_id:  # If no ID is present, generate one
                file_id = str(uuid.uuid4())
                file_detail['id'] = file_id

            # Update or add the file detail in the map
            file_details_map[file_id] = file_detail

        # Convert the map back to a list
        file_details = list(file_details_map.values())

        # Save the updated file details back to the session
        request.session['file_details'] = file_details

        return JsonResponse({'message': 'File details saved'})
    else:
        return JsonResponse({'error': 'Invalid request method'})