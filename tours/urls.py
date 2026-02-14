from django.urls import path
from . import views

urlpatterns = [
    # --- Public Pages ---
    path('', views.home, name='home'),  # The Homepage
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),

    # --- Admin Tour Management ---
    path('admin-panel/tours/', views.admin_tour_list, name='admin_tour_list'),
    path('admin-panel/tours/add/', views.admin_add_tour, name='admin_add_tour'),
    path('admin-panel/tours/edit/<int:tour_id>/', views.admin_edit_tour, name='admin_edit_tour'),
    path('admin-panel/tours/delete/<int:tour_id>/', views.admin_delete_tour, name='admin_delete_tour'),
]