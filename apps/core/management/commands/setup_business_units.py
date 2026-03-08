from django.core.management.base import BaseCommand


BUSINESS_UNITS = [
    ('CAFE', 'Harhurum Café', 'cafe'),
    ('REST', 'Harhurum Restaurant', 'restaurant'),
    ('TAIL', 'Harhurum Tailoring', 'tailoring'),
    ('WHS', 'Harhurum Warehouse & Retail', 'warehouse'),
]


class Command(BaseCommand):
    help = 'Set up default business units'

    def handle(self, *args, **options):
        from apps.core.models import BusinessUnit
        from apps.warehouse.models import Warehouse
        created_count = 0
        for code, name, unit_type in BUSINESS_UNITS:
            unit, created = BusinessUnit.objects.get_or_create(
                code=code, defaults={'name': name, 'unit_type': unit_type}
            )
            if created:
                created_count += 1
                Warehouse.objects.get_or_create(
                    business_unit=unit,
                    name=f'{name} Main Store',
                    defaults={'location_type': 'main'}
                )
        self.stdout.write(self.style.SUCCESS(
            f'Business units setup complete. {created_count} units created.'
        ))
