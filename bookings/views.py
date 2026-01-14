from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta

# Models & Forms
from tours.models import Tour, TourDate
from .models import Booking
from .forms import BookingForm
from .utils import render_to_pdf 

# --- BOOKING STEP 1: FILL FORM (No DB Save yet) ---
@login_required
def book_tour(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, tour=tour)
        if form.is_valid():
            data = form.cleaned_data
            
            # Save data to Session (Temporary storage)
            request.session['booking_data'] = {
                'tour_id': tour.id,
                'tour_date_id': data['tour_date'].id,
                'number_of_people': data['number_of_people'],
                'price_per_person': float(tour.price)
            }
            return redirect('payment_page')
            
    else:
        form = BookingForm(tour=tour)

    return render(request, 'book_tour.html', {'form': form, 'tour': tour})


# --- BOOKING STEP 2: PAYMENT & CREATE DB RECORD ---
@login_required
def payment_page(request):
    booking_data = request.session.get('booking_data')
    
    if not booking_data:
        messages.error(request, "No booking in progress.")
        return redirect('home')

    tour = get_object_or_404(Tour, id=booking_data['tour_id'])
    total_price = booking_data['price_per_person'] * booking_data['number_of_people']

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        
        if transaction_id:
            tour_date = get_object_or_404(TourDate, id=booking_data['tour_date_id'])
            
            # Create the actual booking 
            # Note: status defaults to 'Pending' and payment_status to 'Pending' based on your model
            Booking.objects.create(
                user=request.user,
                tour=tour,
                tour_date=tour_date,
                number_of_people=booking_data['number_of_people'],
                total_price=total_price,
                transaction_id=transaction_id,
            )
            
            # Clear the session
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


# --- ADMIN: MANAGE ALL BOOKINGS ---
@staff_member_required
def admin_booking_list(request):
    bookings = Booking.objects.all().order_by('-booking_date')
    
    # --- FILTERS ---
    status_filter = request.GET.get('status')
    query = request.GET.get('q')
    start_date = request.GET.get('start_date') # <--- NEW
    end_date = request.GET.get('end_date')     # <--- NEW

    # 1. Apply Status Filter
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # 2. Apply Search
    if query:
        bookings = bookings.filter(
            user__username__icontains=query
        ) | bookings.filter(
            tour__name__icontains=query
        ) | bookings.filter(id__icontains=query)

    # 3. Apply Date Filter (NEW CODE)
    if start_date:
        bookings = bookings.filter(booking_date__date__gte=start_date)
    if end_date:
        bookings = bookings.filter(booking_date__date__lte=end_date)

    context = {
        'bookings': bookings,
        'current_status': status_filter,
        'start_date': start_date, # Pass back to template so inputs don't clear
        'end_date': end_date,     # Pass back to template
    }
    return render(request, 'admin/booking_list.html', context)


# --- NEW: UNIFIED ADMIN ACTION VIEW ---
@staff_member_required
def admin_update_booking_status(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id)

    # --- PHASE 1: INITIAL VERIFICATION ---
    if action == 'verify_payment':
        booking.status = 'Confirmed'
        booking.payment_status = 'Paid'
        messages.success(request, f"Booking #{booking.id} verified and confirmed!")
        
    elif action == 'reject_payment':
        booking.status = 'Cancelled'
        booking.payment_status = 'Rejected'
        messages.warning(request, f"Payment for Booking #{booking.id} rejected.")

    # --- PHASE 2: POST-CONFIRMATION ACTIONS ---
    elif action == 'mark_completed':
        booking.status = 'Completed'
        # Payment status remains 'Paid'
        messages.success(request, f"Tour #{booking.id} marked as Completed!")
        
    elif action == 'refund_cancel':
        booking.status = 'Cancelled'
        booking.payment_status = 'Refunded'
        messages.info(request, f"Booking #{booking.id} cancelled and marked as Refunded.")

    booking.save()
    
    # Return to the booking list
    return redirect('admin_booking_list')


# --- TICKET DOWNLOAD ---
@login_required
def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security: Only allow Owner or Staff
    if request.user != booking.user and not request.user.is_staff:
        return HttpResponse("You are not authorized to view this ticket.", status=403)
    
    # Security: Only allow if Confirmed
    if booking.status != 'Confirmed':
         return HttpResponse("Ticket is only available for Confirmed bookings.", status=400)

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


from django.db.models import Sum

@staff_member_required
def admin_payment_report(request):
    payments = Booking.objects.all().order_by('-booking_date')

    # --- FILTERS ---
    status_filter = request.GET.get('status')
    start_date = request.GET.get('start_date') # <--- NEW
    end_date = request.GET.get('end_date')     # <--- NEW
    query = request.GET.get('q')

    # 1. Apply Status Filter
    if status_filter:
        payments = payments.filter(payment_status=status_filter)

    # 2. Apply Date Filter (NEW CODE)
    if start_date:
        payments = payments.filter(booking_date__date__gte=start_date)
    if end_date:
        payments = payments.filter(booking_date__date__lte=end_date)

    # 3. Apply Text Search
    if query:
        payments = payments.filter(
            user__username__icontains=query
        ) | payments.filter(
            transaction_id__icontains=query
        ) | payments.filter(id__icontains=query)

    # 4. Calculate Totals (AFTER filtering)
    total_revenue = Booking.objects.filter(payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    report_total = payments.aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'report_total': report_total,
        'current_status': status_filter,
        'start_date': start_date, 
        'end_date': end_date,     
    }
    return render(request, 'admin/payment_report.html', context)