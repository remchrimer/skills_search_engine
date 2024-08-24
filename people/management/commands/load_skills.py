import csv
from django.core.management.base import BaseCommand
from people.models import Skill

class Command(BaseCommand):
    help = 'Import skills from skills.csv'

    def handle(self, *args, **kwargs):
        with open('data/skills.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Skill.objects.create(
                    skill_id=row['data/id'],
                    name=row['data/name'],
                    info_url=row['data/infoUrl'],
                    skill_type_id=row['data/type/id'],
                    skill_type_name=row['data/type/name']
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported skills'))
