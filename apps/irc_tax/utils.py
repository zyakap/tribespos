def get_upcoming_tax_deadlines(months_ahead: int = 3) -> list:
    from datetime import date
    import calendar
    today = date.today()
    deadlines = []
    for offset in range(months_ahead + 1):
        year = today.year + (today.month + offset - 1) // 12
        month = (today.month + offset - 1) % 12 + 1
        if month == 12:
            gst_year, gst_month = year + 1, 1
        else:
            gst_year, gst_month = year, month + 1
        deadlines.append({
            'type': 'GST', 'description': f"GST Return — {date(year, month, 1).strftime('%B %Y')}",
            'due_date': date(gst_year, gst_month, 21), 'period': f"{year:04d}-{month:02d}", 'colour': 'blue',
        })
        if month == 12:
            swt_year, swt_month = year + 1, 1
        else:
            swt_year, swt_month = year, month + 1
        deadlines.append({
            'type': 'SWT', 'description': f"SWT Remittance — {date(year, month, 1).strftime('%B %Y')}",
            'due_date': date(swt_year, swt_month, 7), 'period': f"{year:04d}-{month:02d}", 'colour': 'orange',
        })
    current_year = today.year
    for quarter, due in [(1, date(current_year, 3, 31)), (2, date(current_year, 6, 30)),
                          (3, date(current_year, 9, 30)), (4, date(current_year, 12, 31))]:
        if due >= today:
            deadlines.append({
                'type': 'CIT_PROVISIONAL', 'description': f"Provisional Tax Q{quarter} — {current_year}",
                'due_date': due, 'period': f"{current_year}-Q{quarter}", 'colour': 'red',
            })
    cit_due = date(today.year, 4, 30)
    if cit_due >= today:
        deadlines.append({
            'type': 'CIT_ANNUAL', 'description': f"CIT Annual Return — FY{today.year - 1}",
            'due_date': cit_due, 'period': str(today.year - 1), 'colour': 'purple',
        })
    return sorted(deadlines, key=lambda x: x['due_date'])
