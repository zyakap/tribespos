from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import JournalEntry, Account, ARInvoice
from .reports import generate_pl, generate_trial_balance


@login_required
def journal_list(request):
    qs = JournalEntry.objects.select_related('fiscal_period').order_by('-entry_date')[:100]
    return render(request, 'accounting/journal_list.html', {'entries': qs})


@login_required
def journal_detail(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    return render(request, 'accounting/journal_detail.html', {'entry': entry})


@login_required
def pl_report(request):
    from datetime import date
    today = date.today()
    start = date(today.year, 1, 1)
    end = today
    if request.GET.get('start'):
        start = date.fromisoformat(request.GET['start'])
    if request.GET.get('end'):
        end = date.fromisoformat(request.GET['end'])
    pl = generate_pl(start, end)
    return render(request, 'accounting/pl_report.html', {'pl': pl, 'start': start, 'end': end})


@login_required
def trial_balance(request):
    rows = generate_trial_balance()
    return render(request, 'accounting/trial_balance.html', {'rows': rows})


@login_required
def coa_list(request):
    accounts = Account.objects.filter(is_active=True).order_by('code')
    return render(request, 'accounting/coa_list.html', {'accounts': accounts})
