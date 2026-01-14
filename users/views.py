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
    pending_bookings = Booking.objects.filter(status='Pending').count()
    confirmed_bookings = Booking.objects.filter(status='Confirmed').count() 
    cancelled_bookings = Booking.objects.filter(status='Cancelled').count() 

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
    # 1. Get the correct User model (Best Practice)
    User = get_user_model() 

    # 2. Get all users
    users = User.objects.all().order_by('-date_joined')
    
    # 3. Check for filters
    role_filter = request.GET.get('role')
    query = request.GET.get('q')

    # 4. Apply Role Filter (Using is_staff)
    if role_filter == 'admin':
        users = users.filter(is_staff=True)
    elif role_filter == 'customer':
        users = users.filter(is_staff=False)

    # 5. Apply Search
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    context = {
        'users': users,
        'current_role': role_filter
    }
    return render(request, 'admin/user_list.html', context)


from django.db.models import Sum

@staff_member_required
def admin_dashboard(request):
    bookings = Booking.objects.all()
    
    # --- 1. BOOKING COUNTS ---
    stats = {
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='Confirmed').count(),
        'pending_bookings': bookings.filter(status='Pending').count(),
        'cancelled_bookings': bookings.filter(status='Cancelled').count(),
        'completed_bookings': bookings.filter(status='Completed').count(), # New
    }

    # --- 2. REVENUE CALCULATIONS ---
    # Total Realized Revenue (Only 'Paid' payments)
    revenue = bookings.filter(payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Pending Payments (Money stuck in limbo)
    pending_pay_amt = bookings.filter(payment_status='Pending').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_pay_cnt = bookings.filter(payment_status='Pending').count()
    
    # Refunded (Money sent back)
    refunded_pay_amt = bookings.filter(payment_status='Refunded').aggregate(Sum('total_price'))['total_price__sum'] or 0
    refunded_pay_cnt = bookings.filter(payment_status='Refunded').count()

    # Rejected (Money blocked)
    rejected_pay_amt = bookings.filter(payment_status='Rejected').aggregate(Sum('total_price'))['total_price__sum'] or 0
    rejected_pay_cnt = bookings.filter(payment_status='Rejected').count()

    context = {
        **stats, # Unpack booking stats
        'total_revenue': revenue,
        'pending_pay_amt': pending_pay_amt,
        'pending_pay_cnt': pending_pay_cnt,
        'refunded_pay_amt': refunded_pay_amt,
        'refunded_pay_cnt': refunded_pay_cnt,
        'rejected_pay_amt': rejected_pay_amt,
        'rejected_pay_cnt': rejected_pay_cnt,
    }
    return render(request, 'admin_dashboard.html', context)