from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.forms import inlineformset_factory

from .models import Tour, TourDate, TourImage
from .forms import TourForm, TourDateForm  # We will create this file next

# ==========================================
# 1. PUBLIC VIEWS (For Customers)
# ==========================================

def home(request):
    """
    The Homepage.
    Displays all ACTIVE tours and handles the search bar.
    """
    # Only show active tours to customers
    tours = Tour.objects.filter(is_active=True).order_by('name')
    
    # Search Logic
    query = request.GET.get('q')
    if query:
        tours = tours.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )
        
    return render(request, 'home.html', {'tours': tours})


def tour_detail(request, tour_id):
    """
    Detailed view of a single tour package.
    """
    tour = get_object_or_404(Tour, pk=tour_id)
    
    # Filter dates: Only show dates that are TODAY or in the FUTURE.
    # We don't want users booking a trip that happened last week!
    available_dates = tour.dates.filter(start_date__gte=date.today()).order_by('start_date')
    
    return render(request, 'tour_detail.html', {
        'tour': tour, 
        'available_dates': available_dates
    })


# ==========================================
# 2. HELPER: FORMSET FACTORIES
# ==========================================
# These allow us to edit Dates and Images on the same page as the Tour.

TourDateFormSet = inlineformset_factory(
    Tour, TourDate, 
    form=TourDateForm, 
    extra=0,            # Don't show empty extra rows by default
    can_delete=True     # Allow admin to delete a date
)

TourImageFormSet = inlineformset_factory(
    Tour, TourImage, 
    fields=('image',), 
    extra=0, 
    can_delete=True
)


# ==========================================
# 3. ADMIN VIEWS (Management)
# ==========================================

@staff_member_required
def admin_tour_list(request):
    """
    Lists all tours (Active and Inactive) for the Admin.
    """
    tours = Tour.objects.all().order_by('-created_at')
    
    # Admin Search
    query = request.GET.get('q')
    if query:
        tours = tours.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query)
        )
        
    return render(request, 'admin/tour_list.html', {'tours': tours})


@staff_member_required
def admin_add_tour(request):
    """
    Create a new Tour Package + Dates + Images.
    """
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        date_formset = TourDateFormSet(request.POST, prefix='dates')
        image_formset = TourImageFormSet(request.POST, request.FILES, prefix='gallery_images')

        if form.is_valid() and date_formset.is_valid() and image_formset.is_valid():
            tour = form.save()
            
            # Save Formsets (Link them to the new tour)
            date_formset.instance = tour
            date_formset.save()
            
            image_formset.instance = tour
            image_formset.save()
            
            return redirect('admin_tour_list')
    else:
        form = TourForm()
        date_formset = TourDateFormSet(prefix='dates')
        image_formset = TourImageFormSet(prefix='gallery_images')

    context = {
        'form': form, 
        'date_formset': date_formset, 
        'image_formset': image_formset, 
        'title': 'Add New Tour'
    }
    return render(request, 'admin/tour_form.html', context)


@staff_member_required
def admin_edit_tour(request, tour_id):
    """
    Edit an existing Tour Package.
    Hides past dates to keep the form clean.
    """
    tour = get_object_or_404(Tour, pk=tour_id)
    
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour)
        
        # We filter the QuerySet so the formset only handles FUTURE dates.
        # This prevents the admin from accidentally deleting old historical data.
        date_formset = TourDateFormSet(
            request.POST, 
            instance=tour, 
            prefix='dates',
            queryset=TourDate.objects.filter(start_date__gte=date.today())
        )
        image_formset = TourImageFormSet(request.POST, request.FILES, instance=tour, prefix='gallery_images')

        if form.is_valid() and date_formset.is_valid() and image_formset.is_valid():
            form.save()
            date_formset.save()
            image_formset.save()
            return redirect('admin_tour_list')
    else:
        form = TourForm(instance=tour)
        
        # Load formset with future dates only
        date_formset = TourDateFormSet(
            instance=tour, 
            prefix='dates',
            queryset=TourDate.objects.filter(start_date__gte=date.today())
        )
        image_formset = TourImageFormSet(instance=tour, prefix='gallery_images')

    context = {
        'form': form, 
        'date_formset': date_formset, 
        'image_formset': image_formset, 
        'title': 'Edit Tour'
    }
    return render(request, 'admin/tour_form.html', context)


@staff_member_required
def admin_delete_tour(request, tour_id):
    """
    Delete a Tour Package.
    """
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        tour.delete()
        return redirect('admin_tour_list')
    return render(request, 'admin/tour_confirm_delete.html', {'tour': tour})