from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from bookings.models import Booking
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required 
from tours.models import Tour
from django.db.models import Q
from django.contrib.auth import get_user_model 
User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    # Fetch bookings for THIS user only, ordered by newest first
    my_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    return render(request, 'dashboard.html', {'bookings': my_bookings})

@staff_member_required
def admin_dashboard(request):
    # 1. Fetch Key Stats
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Status Counts
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count() 
    cancelled_bookings = Booking.objects.filter(status='cancelled').count() 

    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings, 
        'cancelled_bookings': cancelled_bookings, 
    }
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def admin_user_list(request):
    users = User.objects.all().order_by('-date_joined')
    
    # 1. FILTER BY ROLE
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
        
    # 2. SEARCH (Username, Email, or Phone)
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )

    context = {
        'users': users,
        'current_role': role_filter,
    }
    return render(request, 'admin/user_list.html', context)