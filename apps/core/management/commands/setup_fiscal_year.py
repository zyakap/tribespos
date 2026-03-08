from django.core.management.base import BaseCommand
from datetime import date


class Command(BaseCommand):
    help = 'Set up current fiscal year and monthly periods'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=date.today().year)

    def handle(self, *args, **options):
        from apps.accounting.models import FiscalYear, FiscalPeriod
        import calendar
        year = options['year']
        fy, created = FiscalYear.objects.get_or_create(
            name=f'FY {year}',
            defaults={'start_date': date(year, 1, 1), 'end_date': date(year, 12, 31)}
        )
        for month in range(1, 13):
            _, last_day = calendar.monthrange(year, month)
            month_name = date(year, month, 1).strftime('%b %Y')
            FiscalPeriod.objects.get_or_create(
                fiscal_year=fy,
                name=month_name,
                defaults={
                    'start_date': date(year, month, 1),
                    'end_date': date(year, month, last_day),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'FY {year} and 12 monthly periods created.'))
