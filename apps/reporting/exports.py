from io import BytesIO
import openpyxl
from django.http import HttpResponse


def export_to_excel(queryset, headers: list, row_getter, filename='export.xlsx') -> HttpResponse:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for obj in queryset:
        ws.append(row_getter(obj))
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
