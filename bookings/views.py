from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Q
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, date

# Models & Forms
from tours.models import Tour, TourDate
from .models import Booking
from .forms import BookingForm
from .utils import render_to_pdf  # We will create this utility file next

# ==========================================
# 1. CUSTOMER BOOKING FLOW
# ==========================================

@login_required
def book_tour(request, tour_id):
    """
    Step 1: User selects a Date and Number of People.
    We don't save to DB yet; we save to Session to prevent 'ghost' bookings.
    """
    tour = get_object_or_404(Tour, id=tour_id)
    
    if request.method == 'POST':
        # Pass 'tour' to form so it can validate if the date belongs to this tour
        form = BookingForm(request.POST, tour=tour)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Save to Session (Temporary Storage)
            request.session['booking_data'] = {
                'tour_id': tour.id,
                'tour_date_id': data['tour_date'].id, 
                'number_of_people': data['number_of_people'],
                'price_per_person': float(tour.price) # Convert Decimal to float for JSON
            }
            return redirect('payment_page')
            
    else:
        # Pass 'tour' to filter the date dropdown to only show THIS tour's dates
        form = BookingForm(tour=tour)

    return render(request, 'book_tour.html', {'form': form, 'tour': tour})


@login_required
def payment_page(request):
    """
    Step 2: User enters Transaction ID.
    Step 3: We create the actual Booking in the Database.
    """
    booking_data = request.session.get('booking_data')
    
    # Security: If they try to skip Step 1, send them back
    if not booking_data:
        messages.error(request, "No booking in progress.")
        return redirect('home')

    tour = get_object_or_404(Tour, id=booking_data['tour_id'])
    total_price = booking_data['price_per_person'] * booking_data['number_of_people']

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        
        if transaction_id:
            # Fetch the actual Date Object
            tour_date = get_object_or_404(TourDate, id=booking_data['tour_date_id'])
            
            # Create the Database Record
            Booking.objects.create(
                user=request.user,
                tour=tour,
                tour_date=tour_date,
                number_of_people=booking_data['number_of_people'],
                total_price=total_price,
                transaction_id=transaction_id,
                status='Pending',        # Admin needs to verify
                payment_status='Pending' # Admin needs to verify money
            )
            
            # Clear the session so they can't submit twice
            del request.session['booking_data']
            
            messages.success(request, "Payment Submitted! Please wait for Admin Verification.")
            return redirect('dashboard')
        else:
            messages.error(request, "Transaction ID is mandatory!")

    context = {
        'tour': tour,
        'total_price': total_price,
        'booking_data': booking_data
    }
    return render(request, 'payment.html', context)


@login_required
def download_ticket(request, booking_id):
    """
    Generates a PDF Ticket for Confirmed or Completed Bookings.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security: Only Owner or Admin can download
    if request.user != booking.user and not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    # FIX: Allow ticket download if status is 'Confirmed' OR 'Completed'
    if booking.status not in ['Confirmed', 'Completed']:
         return HttpResponse("Ticket is only available for Confirmed or Completed bookings.", status=400)

    data = {
        'booking': booking,
        'tour': booking.tour,
        'user': booking.user,
    }
    
    pdf = render_to_pdf('ticket_pdf.html', data)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Ticket_{booking.id}_{booking.tour.name}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
        
    return HttpResponse("Error Rendering PDF", status=400)

# ==========================================
# 2. ADMIN MANAGEMENT VIEWS
# ==========================================

@staff_member_required
def admin_booking_list(request):
    """
    View all bookings with advanced filters (Status, Date, Search).
    """
    bookings = Booking.objects.all().order_by('-booking_date')
    
    # Get Filter Params
    status_filter = request.GET.get('status')
    query = request.GET.get('q')
    start_date = request.GET.get('start_date') 
    end_date = request.GET.get('end_date')     

    # Apply Filters
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    if query:
        bookings = bookings.filter(
            Q(user__username__icontains=query) |
            Q(tour__name__icontains=query) |
            Q(id__icontains=query)
        )

    if start_date:
        bookings = bookings.filter(booking_date__date__gte=start_date)
    if end_date:
        bookings = bookings.filter(booking_date__date__lte=end_date)

    context = {
        'bookings': bookings,
        'current_status': status_filter,
        'start_date': start_date, 
        'end_date': end_date,     
    }
    return render(request, 'admin/booking_list.html', context)


@staff_member_required
def admin_update_booking_status(request, booking_id, action):
    """
    Handles logic for Verify, Reject, Complete, Refund buttons.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # 1. Verification Phase
    if action == 'verify_payment':
        booking.status = 'Confirmed'
        booking.payment_status = 'Paid'
        messages.success(request, f"Booking #{booking.id} verified and confirmed!")
        
    elif action == 'reject_payment':
        booking.status = 'Cancelled'
        booking.payment_status = 'Rejected'
        messages.warning(request, f"Payment for Booking #{booking.id} rejected.")

    # 2. Post-Trip Phase
    elif action == 'mark_completed':
        booking.status = 'Completed'
        messages.success(request, f"Tour #{booking.id} marked as Completed!")
        
    elif action == 'refund_cancel':
        booking.status = 'Cancelled'
        booking.payment_status = 'Refunded'
        messages.info(request, f"Booking #{booking.id} cancelled and marked as Refunded.")

    booking.save()
    return redirect('admin_booking_list')


@staff_member_required
def admin_payment_report(request):
    """
    Financial Report View for Admins.
    """
    payments = Booking.objects.all().order_by('-booking_date')

    # Filters
    status_filter = request.GET.get('status')
    start_date = request.GET.get('start_date') 
    end_date = request.GET.get('end_date')     
    query = request.GET.get('q')

    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    if start_date:
        payments = payments.filter(booking_date__date__gte=start_date)
    if end_date:
        payments = payments.filter(booking_date__date__lte=end_date)
    if query:
        payments = payments.filter(
            Q(user__username__icontains=query) |
            Q(transaction_id__icontains=query)
        )

    # Totals
    total_revenue = Booking.objects.filter(payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    report_total = payments.aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'report_total': report_total,
        'current_status': status_filter,
    }
    return render(request, 'admin/payment_report.html', context)