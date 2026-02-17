"""
BondVoyage Main URL Configuration

Refined & Modularized:
- Delegates specific URLs to their respective apps (tours, users, bookings).
- Handles global Media serving (Images).
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Handles: Register, Login, Logout, Dashboard
    path('', include('users.urls')), 

    # Handles: Home Page, Tour Details, Admin Tour Management
    path('', include('tours.urls')), 

    # Handles: Booking logic, Payments, Ticket Downloads
    path('', include('bookings.urls')), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)