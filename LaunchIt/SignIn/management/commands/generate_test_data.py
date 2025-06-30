from django.core.management.base import BaseCommand
from django.utils import timezone
from SignIn.models import VisitReason, IndividualSignIn, EventSignIn
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Generates test data for sign-in models'

    def add_arguments(self, parser):
        parser.add_argument('--individuals', type=int, default=20, 
                            help='Number of individual sign-ins to create')
        parser.add_argument('--events', type=int, default=10,
                            help='Number of event sign-ins to create')
        parser.add_argument('--clear', action='store_true',
                            help='Clear existing sign-in data before generating new data')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing sign-in data...'))
            IndividualSignIn.objects.all().delete()
            EventSignIn.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing sign-in data cleared.'))

        # Ensure we have visit reasons
        self._ensure_visit_reasons()

        # Generate individual sign-ins
        self._generate_individual_signins(options['individuals'])
        
        # Generate event sign-ins
        self._generate_event_signins(options['events'])
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully generated {options['individuals']} individual sign-ins and {options['events']} event sign-ins")
        )

    def _ensure_visit_reasons(self):
        """Ensure we have some visit reasons in the database"""
        reasons = [
            'Business Meeting', 
            'Conference', 
            'Workshop', 
            'Tour', 
            'Interview',
            'Maintenance',
            'Delivery',
            'Social Event',
            'Training Session',
            'Office Hours'
        ]
        
        for reason_name in reasons:
            VisitReason.objects.get_or_create(name=reason_name)
        
        self.stdout.write(self.style.SUCCESS(f'Ensured {len(reasons)} visit reasons exist'))

    def _generate_individual_signins(self, count):
        """Generate individual sign-ins with varied data"""
        self.stdout.write(f'Generating {count} individual sign-ins...')
        
        # Get all reasons
        reasons = list(VisitReason.objects.all())
        
        # First and last names for random name generation
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Maria', 
                      'James', 'Lisa', 'Carlos', 'Emma', 'William', 'Olivia', 'Daniel', 'Sophia',
                      'Matthew', 'Ava', 'Aiden', 'Isabella', 'Alexander', 'Mia', 'Ethan', 'Charlotte']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                     'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Harris', 'Clark', 'Lewis']
        
        today = timezone.now().date()
        
        for i in range(count):
            # Generate a random date in the last 90 days
            days_ago = random.randint(0, 90)
            sign_in_date = today - timedelta(days=days_ago)
            
            # Generate a random name
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            # Select a random reason
            reason = random.choice(reasons)
            
            # Create the sign-in
            IndividualSignIn.objects.create(
                name=name,
                date=sign_in_date,
                reason=reason
            )

    def _generate_event_signins(self, count):
        """Generate event sign-ins with varied data"""
        self.stdout.write(f'Generating {count} event sign-ins...')
        
        # Get all reasons
        reasons = list(VisitReason.objects.all())
        
        # Event names for random generation
        event_organizers = [
            'Tech Conference', 'Marketing Team', 'HR Department', 'Finance Group',
            'Product Team', 'Executive Board', 'Sales Department', 'IT Support',
            'Research Division', 'Customer Service', 'External Partners',
            'Community Outreach', 'Training Department', 'Quality Assurance',
            'Strategic Planning'
        ]
        
        today = timezone.now().date()
        
        for i in range(count):
            # Generate a random date in the last 180 days
            days_ago = random.randint(0, 180)
            sign_in_date = today - timedelta(days=days_ago)
            
            # Generate a random organizer name
            organizer_name = random.choice(event_organizers)
            
            # Select a random reason
            reason = random.choice(reasons)
            
            # Generate a random attendee count between 2 and 150
            attendee_count = random.randint(2, 150)
            
            # Create the event sign-in
            EventSignIn.objects.create(
                organizer_name=organizer_name,
                date=sign_in_date,
                reason=reason,
                attendee_count=attendee_count
            )
