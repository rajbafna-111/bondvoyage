from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from tours.models import Tour
from .models import Booking, Tour, TourDate
from .forms import BookingForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.contrib import messages
from .utils import render_to_pdf 
from django.http import HttpResponse

# --- BOOKING STEP 1: FILL FORM (No DB Save yet) ---
@login_required
def book_tour(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, tour=tour)
        if form.is_valid():
            data = form.cleaned_data
            
            # Save to Session
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


# --- USER CANCELLATION ---
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # FIX 1: Check for 'Pending' (Capital P)
    if booking.status == 'Pending':
        # FIX 2: Set to 'Cancelled' (Capital C)
        booking.status = 'Cancelled'
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
    
    return redirect('dashboard')


# --- ADMIN: MANAGE ALL BOOKINGS ---
@staff_member_required
def admin_booking_list(request):
    bookings = Booking.objects.all().order_by('-booking_date')
    
    # 1. FILTERING (Tabs)
    status_filter = request.GET.get('status')
    
    if status_filter:
        # FIX 3: Convert URL param (e.g., 'pending') to DB format ('Pending')
        # .capitalize() turns "pending" -> "Pending"
        db_status = status_filter.capitalize()
        bookings = bookings.filter(status=db_status)
        
    # 2. SEARCHING
    query = request.GET.get('q')
    if query:
        bookings = bookings.filter(
            Q(user__username__icontains=query) |
            Q(tour__name__icontains=query) |
            Q(transaction_id__icontains=query) # Added searching by Transaction ID too!
        )

    context = {
        'bookings': bookings,
        'current_status': status_filter, 
    }
    return render(request, 'admin/booking_list.html', context)


# --- ADMIN: APPROVE BOOKING ---
@staff_member_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # FIX 4: Set to 'Confirmed' (Capital C)
    booking.status = 'Confirmed'
    booking.save()
    messages.success(request, "Booking Confirmed!")
    return redirect('admin_booking_list')


# --- ADMIN: REJECT/CANCEL BOOKING ---
@staff_member_required
def admin_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # FIX 5: Set to 'Cancelled' (Capital C)
    booking.status = 'Cancelled'
    booking.save()
    messages.success(request, "Booking Cancelled.")
    return redirect('admin_booking_list')


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
            
            # Create the actual booking now
            Booking.objects.create(
                user=request.user,
                tour=tour,
                tour_date=tour_date,
                number_of_people=booking_data['number_of_people'],
                total_price=total_price,
                transaction_id=transaction_id,
                status='Pending' # Correct (Capital P)
            )
            
            del request.session['booking_data']
            
            messages.success(request, "Payment Submitted! Booking Created Successfully.")
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
    # Get the booking, ensure it belongs to the user (or is staff)
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security: Only allow Owner or Staff to view
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
    
    # Render the PDF
    pdf = render_to_pdf('ticket_pdf.html', data)
    
    # Force download (optional: remove 'attachment;' to view in browser instead)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Ticket_{booking.id}_{booking.tour.name}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
        
    return HttpResponse("Error Rendering PDF", status=400)