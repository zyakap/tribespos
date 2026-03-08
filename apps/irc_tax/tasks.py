from celery import shared_task
from datetime import date


@shared_task
def auto_generate_monthly_returns():
    today = date.today()
    if today.month == 1:
        year, month = today.year - 1, 12
    else:
        year, month = today.year, today.month - 1
    from apps.irc_tax.services.gst_service import generate_gst_return
    from apps.irc_tax.services.swt_service import generate_swt_remittance
    generate_gst_return(year, month)
    generate_swt_remittance(year, month)


@shared_task
def check_tax_deadline_alerts():
    from django.conf import settings
    from django.core.mail import send_mail
    from .utils import get_upcoming_tax_deadlines
    deadlines = get_upcoming_tax_deadlines(months_ahead=1)
    today = date.today()
    alert_email = settings.HARHURUM_CONFIG.get('TAX_ALERT_EMAIL', '')
    if not alert_email:
        return
    for dl in deadlines:
        days_until = (dl['due_date'] - today).days
        if days_until <= 7:
            status = 'OVERDUE' if days_until < 0 else f"DUE IN {days_until} DAYS"
            send_mail(
                subject=f"[Harhurum Tax Alert] {dl['type']} {status} — {dl['description']}",
                message=f"Tax Compliance Alert\n\n{dl['description']}\nDue Date: {dl['due_date'].strftime('%d %B %Y')}\nStatus: {status}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[alert_email],
                fail_silently=True,
            )
