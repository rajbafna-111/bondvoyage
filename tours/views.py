from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .models import Tour
from .forms import TourForm

def home(request):
    # Start with all active tours
    tours = Tour.objects.filter(is_active=True)
    
    # Check if there is a search query in the URL (e.g., /?q=paris)
    query = request.GET.get('q')
    
    if query:
        # Filter: Name contains query OR Location contains query
        tours = tours.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )
    
    return render(request, 'home.html', {'tours': tours})

# Add this new function
def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    return render(request, 'tour_detail.html', {'tour': tour})

# --- ADMIN: LIST ALL PACKAGES ---
@staff_member_required
def admin_tour_list(request):
    tours = Tour.objects.all().order_by('-created_at')
    
    # Search Logic
    query = request.GET.get('q')
    if query:
        tours = tours.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query)
        )
    
    return render(request, 'admin/tour_list.html', {'tours': tours})

# --- ADMIN: ADD NEW PACKAGE ---
@staff_member_required
def admin_add_tour(request):
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES) # request.FILES is needed for images
        if form.is_valid():
            form.save()
            return redirect('admin_tour_list')
    else:
        form = TourForm()
    return render(request, 'admin/tour_form.html', {'form': form, 'title': 'Add New Tour'})

# --- ADMIN: EDIT PACKAGE ---
@staff_member_required
def admin_edit_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour) # instance loads existing data
        if form.is_valid():
            form.save()
            return redirect('admin_tour_list')
    else:
        form = TourForm(instance=tour)
    return render(request, 'admin/tour_form.html', {'form': form, 'title': 'Edit Tour'})

# --- ADMIN: DELETE PACKAGE ---
@staff_member_required
def admin_delete_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        tour.delete()
        return redirect('admin_tour_list')
    return render(request, 'admin/tour_confirm_delete.html', {'tour': tour})