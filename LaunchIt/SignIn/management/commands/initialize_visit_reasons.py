from django.core.management.base import BaseCommand
from SignIn.models import VisitReason


class Command(BaseCommand):
    help = 'Initialize default visit reasons'

    def handle(self, *args, **kwargs):
        default_reasons = [
            'Meeting',
            'Interview',
            'Delivery',
            'Conference',
            'Workshop',
            'Tour',
            'Maintenance',
            'Other'
        ]

        created_count = 0
        existing_count = 0

        for reason in default_reasons:
            obj, created = VisitReason.objects.get_or_create(name=reason)
            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized {created_count} visit reasons. '
                f'{existing_count} already existed.'
            )
        )
