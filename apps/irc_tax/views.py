from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import GSTReturn, SWTRemittance, CITReturn
from .utils import get_upcoming_tax_deadlines


@login_required
def tax_dashboard(request):
    deadlines = get_upcoming_tax_deadlines(months_ahead=3)
    recent_gst = GSTReturn.objects.order_by('-return_period')[:6]
    recent_swt = SWTRemittance.objects.order_by('-remittance_month')[:6]
    return render(request, 'irc_tax/dashboard.html', {
        'deadlines': deadlines, 'recent_gst': recent_gst, 'recent_swt': recent_swt
    })


@login_required
def gst_return_list(request):
    returns = GSTReturn.objects.order_by('-return_period')
    return render(request, 'irc_tax/gst_return_list.html', {'returns': returns})


@login_required
def gst_return_detail(request, period):
    gst_return = get_object_or_404(GSTReturn, return_period=period)
    return render(request, 'irc_tax/gst_return_detail.html', {'gst_return': gst_return})


@login_required
def gst_generate(request):
    if request.method == 'POST':
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        from .services.gst_service import generate_gst_return
        gst = generate_gst_return(year, month)
        return JsonResponse({'period': gst.return_period, 'status': gst.status})
    from datetime import date
    return render(request, 'irc_tax/gst_generate.html', {'today': date.today()})


@login_required
def swt_list(request):
    remittances = SWTRemittance.objects.order_by('-remittance_month')
    return render(request, 'irc_tax/swt_list.html', {'remittances': remittances})


@login_required
def cit_return(request, year=None):
    from datetime import date
    if year is None:
        year = date.today().year - 1
    try:
        cit = CITReturn.objects.get(tax_year=year)
    except CITReturn.DoesNotExist:
        cit = None
    return render(request, 'irc_tax/cit_return.html', {'cit': cit, 'year': year})
