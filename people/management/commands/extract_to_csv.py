import csv
from django.core.management.base import BaseCommand
from people.models import Person

class Command(BaseCommand):
    help = 'Export Person data to a CSV file'

    def handle(self, *args, **kwargs):
        file_name = 'data/person_data.csv'
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['unique_id', 'name', 'organization', 'email', 'top_skills', 'other_skills', 'title', 'division', 'program', 'bio'])
            for person in Person.objects.all():
                writer.writerow([
                    person.unique_id,
                    person.name,
                    person.organization,
                    person.email,
                    person.top_skills,
                    person.other_skills,
                    person.title,
                    person.division,
                    person.program,
                    person.bio,
                ])

        self.stdout.write(self.style.SUCCESS(f'Data successfully exported to {file_name}'))