# myapp/management/commands/import_csv.py
import csv
from django.core.management.base import BaseCommand
from people.models import Person

class Command(BaseCommand):
    help = 'Import data from CSV file to MySQL database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        self.import_csv_to_db(csv_file_path)

    def import_csv_to_db(self, csv_file_path):
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['Name']
                unique_id = row['unique_id']
                top_skills = [skill.strip() for skill in row['Top Skills'].split(',')]
                Person.objects.update_or_create(
                    unique_id=unique_id,
                    defaults={
                        'name': name,
                        'email': row.get('Email', 'N/A'),
                        'title': row.get('Title', 'N/A'),
                        'division': row.get('Division', 'N/A'),
                        'program': row.get('Program', 'N/A'),
                        'bio': row.get('Bio', 'N/A'),
                        'top_skills': ', '.join(top_skills),
                        'other_skills': row.get('Other Skills', 'N/A')
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported data from CSV'))
