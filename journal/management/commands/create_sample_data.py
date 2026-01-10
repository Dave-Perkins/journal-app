from django.core.management.base import BaseCommand
from journal.models import Horse, Rider


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create some sample horses
        horses_data = ['Spirit', 'Thunder', 'Luna', 'Midnight']
        
        for horse_name in horses_data:
            horse, created = Horse.objects.get_or_create(name=horse_name)
            if created:
                self.stdout.write(f'Created horse: {horse_name}')
        
        # Create some sample riders for each horse
        riders_data = {
            'Spirit': ['Sarah', 'Emma', 'John'],
            'Thunder': ['Mike', 'Lisa'],
            'Luna': ['Alex', 'Jordan', 'Casey'],
            'Midnight': ['Sam', 'Taylor'],
        }

        for horse_name, rider_names in riders_data.items():
            horse = Horse.objects.get(name=horse_name)
            for rider_name in rider_names:
                rider, created = Rider.objects.get_or_create(
                    name=rider_name,
                    horse=horse
                )
                if created:
                    self.stdout.write(f'Created rider: {rider_name} for {horse_name}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
