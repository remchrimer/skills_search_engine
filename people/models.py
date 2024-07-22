from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    top_skills = models.TextField()
    other_skills = models.TextField()

    def __str__(self):
        return self.name
