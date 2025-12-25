from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views # Import built-in auth views
from tours.views import *
from users.views import * # Import our new view
from bookings.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # <--- Add this line
    path('tour/<int:tour_id>/', tour_detail, name='tour_detail'),
    # Authentication URLs
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('tour/<int:tour_id>/book/', book_tour, name='book_tour'), # <--- Add this
    path('dashboard/', dashboard, name='dashboard'), # <--- Add this line
    path('booking/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'), # <--- Add this

    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('booking/<int:booking_id>/approve/', approve_booking, name='approve_booking'),
    # Admin Package Management
    path('admin-panel/tours/', admin_tour_list, name='admin_tour_list'),
    path('admin-panel/tours/add/', admin_add_tour, name='admin_add_tour'),
    path('admin-panel/tours/edit/<int:tour_id>/', admin_edit_tour, name='admin_edit_tour'),
    path('admin-panel/tours/delete/<int:tour_id>/', admin_delete_tour, name='admin_delete_tour'),
    # Admin Booking Management
    path('admin-panel/bookings/', admin_booking_list, name='admin_booking_list'),
    path('admin-panel/bookings/cancel/<int:booking_id>/', admin_cancel_booking, name='admin_cancel_booking'),
    path('admin-panel/users/', admin_user_list, name='admin_user_list'),
]

# This allows images to show up during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)