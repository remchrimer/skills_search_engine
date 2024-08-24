from django.db import models

class Person(models.Model):
    unique_id = models.CharField(max_length=255, unique=True, default='DEFAULT_ID')
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    email = models.EmailField()
    top_skills = models.TextField()
    other_skills = models.TextField()
    title = models.CharField(max_length=255, blank=True, null=True)
    division = models.CharField(max_length=255, default='Unknown')
    program = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class Skill(models.Model):
    skill_id = models.CharField(max_length=255, unique=True)  # data/id
    name = models.CharField(max_length=255)  # data/name
    info_url = models.URLField(max_length=500, blank=True, null=True)  # data/infoUrl
    skill_type_id = models.CharField(max_length=255, blank=True, null=True)  # data/type/id
    skill_type_name = models.CharField(max_length=255, blank=True, null=True)  # data/type/name

    def __str__(self):
        return self.name
