from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('district/<str:district_name>/', views.district_schemes, name='district_schemes'),
    
    # Custom registration view
    path('register/', views.register, name='register'),
    
    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Password Reset views
    path('password_reset/', views.direct_password_reset, name='password_reset'),
    
    # Chatbot API
    path('api/chat/', views.chatbot_response, name='chatbot_response'),
]
