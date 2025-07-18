from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.docs_list, name='docs_list'),
    path('login/',  auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    path('upload/', views.upload_file, name='upload'),
    path('analyze/<int:doc_id>/', views.analyze_document, name='analyze'),
    path('delete/<int:doc_id>/', views.delete_document, name='delete'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:doc_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/pay/', views.pay_cart, name='pay_cart'),
]