from django.shortcuts import render
from .models import Docs

def docs_list(request):
    docs = Docs.objects.all()
    return render(request, 'docs_list.html', {'docs': docs})