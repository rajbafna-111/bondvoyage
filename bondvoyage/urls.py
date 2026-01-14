from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 
from tours.views import *
from users.views import * 
from bookings.views import *

urlpatterns = [
    # Authentication URLs
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Booking System
    path('tour/<int:tour_id>/', tour_detail, name='tour_detail'),
    path('tour/<int:tour_id>/book/', book_tour, name='book_tour'), 
    path('admin/booking/<int:booking_id>/<str:action>/', admin_update_booking_status, name='admin_booking_action'),
    path('payment/process/', payment_page, name='payment_page'),
    path('booking/<int:booking_id>/ticket/', download_ticket, name='download_ticket'),
    
    #Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Admin Package Management
    path('admin-panel/tours/', admin_tour_list, name='admin_tour_list'),
    path('admin-panel/tours/add/', admin_add_tour, name='admin_add_tour'),
    path('admin-panel/tours/edit/<int:tour_id>/', admin_edit_tour, name='admin_edit_tour'),
    path('admin-panel/tours/delete/<int:tour_id>/', admin_delete_tour, name='admin_delete_tour'),
    
    # Admin Booking Management
    path('admin-panel/bookings/', admin_booking_list, name='admin_booking_list'),
    path('admin-panel/users/', admin_user_list, name='admin_user_list'),
    path('admin-panel/payments/', admin_payment_report, name='admin_payment_report'),

    path('admin/', admin.site.urls),
    path('', home, name='home'),
]

# to show up image
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)