import csv
from django.core.management.base import BaseCommand
from people.models import Person

class Command(BaseCommand):
    help = 'Load data from CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('data/people.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Person.objects.create(
                    name=row['Name'],
                    organization=row['Organization'],
                    email=row['Email'],
                    phone=row['Phone'],
                    top_skills=row['Top Skills'],
                    other_skills=row['Other Skills']
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded data from CSV'))
