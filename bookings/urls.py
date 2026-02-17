from django.urls import path
from . import views

urlpatterns = [
    # Customer Booking Flow
    path('tour/<int:tour_id>/book/', views.book_tour, name='book_tour'),
    path('payment/process/', views.payment_page, name='payment_page'),
    path('booking/<int:booking_id>/ticket/', views.download_ticket, name='download_ticket'),

    # Admin Booking Management
    path('admin-panel/bookings/', views.admin_booking_list, name='admin_booking_list'),
    path('admin-panel/payments/', views.admin_payment_report, name='admin_payment_report'),
    
    # Booking Actions (Approve/Cancel/Reject)
    path('staff/booking/<int:booking_id>/<str:action>/', views.admin_update_booking_status, name='admin_booking_action'),
]