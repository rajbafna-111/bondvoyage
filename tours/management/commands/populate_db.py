import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction # <--- Added for safety
from faker import Faker
from tours.models import Tour, TourDate
from bookings.models import Booking

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        try:
            with transaction.atomic(): # If anything fails, undo everything
                self.stdout.write("1. Cleaning old data...")
                Booking.objects.all().delete()
                TourDate.objects.all().delete()
                Tour.objects.all().delete()
                # Delete customers, but PROTECT the admin/superuser
                User.objects.filter(is_staff=False, is_superuser=False).delete()

                self.stdout.write("2. Creating Users...")
                users = []
                for _ in range(20):
                    email = fake.unique.email()
                    # Add random number to ensure username is unique and doesn't clash with Admin
                    username = email.split('@')[0] + str(random.randint(1000, 9999))
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password="password123",
                        phone_number=fake.phone_number()[:15], # Crop to 15 chars to prevent "too long" error
                        address=fake.address()[:200], # Crop address to be safe
                        role='customer'
                    )
                    users.append(user)

                self.stdout.write("3. Creating Tours...")
                tours = []
                tour_names = [
                    "Swiss Alps Adventure", "Bali Beach Retreat", "Tokyo City Explore", 
                    "Safari in Kenya", "Paris Romantic Getaway", "New York City Break",
                    "Inca Trail Hike", "Santorini Sunset Cruise", "Dubai Luxury Escape",
                    "Great Barrier Reef Dive"
                ]
                
                for name in tour_names:
                    tour = Tour.objects.create(
                        name=name,
                        location=fake.city(),
                        description=fake.text(max_nb_chars=200), # Keep text short enough for DB
                        duration_days=random.randint(3, 14),
                        price=random.randint(500, 5000),
                        is_active=True
                    )
                    tours.append(tour)

                self.stdout.write("4. Creating Dates & Bookings...")
                for tour in tours:
                    for _ in range(5):
                        start_date = timezone.now().date() + timedelta(days=random.randint(1, 90))
                        tour_date = TourDate.objects.create(
                            tour=tour,
                            start_date=start_date,
                            capacity=20
                        )
                        
                        # Random bookings
                        for _ in range(random.randint(0, 3)):
                            user = random.choice(users)
                            people = random.randint(1, 4)
                            Booking.objects.create(
                                user=user,
                                tour=tour,
                                tour_date=tour_date,
                                number_of_people=people,
                                total_price=tour.price * people,
                                status=random.choice(['pending', 'confirmed', 'cancelled'])
                            )

            self.stdout.write(self.style.SUCCESS("Success! Database populated."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERROR FAILED: {str(e)}"))