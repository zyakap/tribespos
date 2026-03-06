from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Set up default GST tax rates'

    def handle(self, *args, **options):
        from apps.accounting.models import TaxRate, Account
        try:
            sales_account = Account.objects.get(code='2100')
            purchase_account = Account.objects.get(code='2110')
        except Account.DoesNotExist:
            self.stdout.write(self.style.WARNING('Run setup_accounts first.'))
            return

        _, created = TaxRate.objects.get_or_create(
            name='GST 10%',
            defaults={
                'rate': 10.00,
                'tax_type': 'gst',
                'sales_account': sales_account,
                'purchase_account': purchase_account,
                'is_default': True,
            }
        )
        TaxRate.objects.get_or_create(name='GST Exempt', defaults={'rate': 0, 'tax_type': 'exempt'})
        TaxRate.objects.get_or_create(name='Zero-Rated', defaults={'rate': 0, 'tax_type': 'zero'})
        self.stdout.write(self.style.SUCCESS('Tax rates setup complete.'))
