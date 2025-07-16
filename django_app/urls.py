from django.urls import path
from . import views

urlpatterns = [
    path('', views.docs_list, name='docs_list'),
    path('upload/', views.upload_file, name='upload'),
    path('analyze/<int:doc_id>/', views.analyze_doc, name='analyze'),
]