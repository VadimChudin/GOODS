from django.urls import path
from . import views

urlpatterns = [
    path('', views.docs_list, name='docs_list'),
]