from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Authentication ---
    path('register/', views.register, name='register'),
    
    # We use Django's built-in Login/Logout views but point them to our templates
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # --- Dashboards ---
    path('dashboard/', views.dashboard, name='dashboard'),             # Customer Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'), # Admin Main Dashboard
    
    # --- Admin User Management ---
    path('admin-panel/users/', views.admin_user_list, name='admin_user_list'),
]