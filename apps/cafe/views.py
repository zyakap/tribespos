from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def cafe_pos(request):
    from apps.pos.views import pos_terminal
    return pos_terminal(request, unit_code='CAFE')
