from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from tours.models import Tour
from .models import Booking
from .forms import BookingForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

@login_required
def book_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, tour_id=tour.id)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.tour = tour

           
            # Manually grab the date from the form and assign it
            booking.tour_date = form.cleaned_data['tour_date']

            booking.save()
            return redirect('dashboard')
            
    else: 
        form = BookingForm(tour_id=tour.id)

    return render(request, 'book_tour.html', {'form': form, 'tour': tour})


@login_required
def cancel_booking(request, booking_id):
    # Get the booking, but ONLY if it belongs to this user
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Only allow cancellation if it's currently 'pending'
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
    
    return redirect('dashboard')




# --- ADMIN: MANAGE ALL BOOKINGS ---
@staff_member_required
def admin_booking_list(request):
    # Start with all bookings, newest first
    bookings = Booking.objects.all().order_by('-booking_date')
    
    # 1. FILTERING (Tabs)
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
        
    # 2. SEARCHING
    query = request.GET.get('q')
    if query:
        bookings = bookings.filter(
            Q(user__username__icontains=query) |
            Q(tour__name__icontains=query)
        )

    context = {
        'bookings': bookings,
        'current_status': status_filter, # To keep the active tab highlighted
    }
    return render(request, 'admin/booking_list.html', context)

# --- ADMIN: APPROVE or CANCEL BOOKING ---
@staff_member_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'confirmed'
    booking.save()
    return redirect('admin_dashboard')

@staff_member_required
def admin_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'cancelled'
    booking.save()
    return redirect('admin_booking_list')