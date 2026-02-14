from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Q

from .forms import CustomUserCreationForm
from bookings.models import Booking

# Get the Custom User model safely
User = get_user_model()

def register(request):
    """
    Handles User Registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    """
    Customer Dashboard: Shows their specific booking history.
    """
    # Redirect Admins to the Admin Dashboard if they land here
    if request.user.is_staff or request.user.role == 'admin':
        return redirect('admin_dashboard')

    # Fetch bookings for THIS user only, ordered by newest first
    my_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    return render(request, 'dashboard.html', {'bookings': my_bookings})


@staff_member_required
def admin_dashboard(request):
    """
    Admin Dashboard: Shows global stats, revenue, and booking statuses.
    """
    bookings = Booking.objects.all()
    
    # --- 1. BOOKING COUNTS ---
    stats = {
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='Confirmed').count(),
        'pending_bookings': bookings.filter(status='Pending').count(),
        'cancelled_bookings': bookings.filter(status='Cancelled').count(),
        'completed_bookings': bookings.filter(status='Completed').count(),
    }

    # --- 2. REVENUE CALCULATIONS ---
    # Total Realized Revenue (Only 'Paid' payments)
    revenue = bookings.filter(payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Financial Status Counts
    # Pending (Money stuck)
    pending_pay_amt = bookings.filter(payment_status='Pending').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_pay_cnt = bookings.filter(payment_status='Pending').count()
    
    # Refunded (Money sent back)
    refunded_pay_amt = bookings.filter(payment_status='Refunded').aggregate(Sum('total_price'))['total_price__sum'] or 0
    refunded_pay_cnt = bookings.filter(payment_status='Refunded').count()

    # Rejected (Money blocked)
    rejected_pay_amt = bookings.filter(payment_status='Rejected').aggregate(Sum('total_price'))['total_price__sum'] or 0
    rejected_pay_cnt = bookings.filter(payment_status='Rejected').count()

    context = {
        **stats, # Unpack the stats dictionary
        'total_revenue': revenue,
        'pending_pay_amt': pending_pay_amt, 'pending_pay_cnt': pending_pay_cnt,
        'refunded_pay_amt': refunded_pay_amt, 'refunded_pay_cnt': refunded_pay_cnt,
        'rejected_pay_amt': rejected_pay_amt, 'rejected_pay_cnt': rejected_pay_cnt,
    }
    return render(request, 'admin_dashboard.html', context)


@staff_member_required
def admin_user_list(request):
    """
    Lists all registered users with filters for Roles and Search.
    """
    users = User.objects.all().order_by('-date_joined')
    
    # Get Filter Params
    role_filter = request.GET.get('role')
    query = request.GET.get('q')

    # 1. Apply Role Filter
    if role_filter == 'admin':
        users = users.filter(role=User.ADMIN)
    elif role_filter == 'customer':
        users = users.filter(role=User.CUSTOMER)

    # 2. Apply Search (Username or Email)
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query)
        )

    context = {
        'users': users,
        'current_role': role_filter
    }
    return render(request, 'admin/user_list.html', context)