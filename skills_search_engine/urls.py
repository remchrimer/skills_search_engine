"""
URL configuration for skills_search_engine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from people.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('search/', search, name='search'),
    path('person/<str:name>/<str:unique_id_part>/', person_detail, name='person_detail'),
    path('get_graph_data/', get_graph_data, name='get_graph_data'),
    path('passcode/', passcode_check, name='passcode_check'),
    path('upload/', upload_resume, name='upload_resume'),
    path('upload_file/', upload_file, name='upload_file'),
    path('save_details/', save_details, name='save_details'),
    path('edit_file/<int:file_index>/', edit_file, name='edit_file'),
    path('save_file_details/', save_file_details, name='save_file_details'),
    path('edit_person/<str:unique_id>/', edit_person, name='edit_person'),
    path('skill-suggestions/', skill_suggestions, name='skill_suggestions'),
]