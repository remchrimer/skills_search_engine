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
