import csv
import random
from datetime import datetime, timedelta

random.seed(42)

cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat"]
provider_types = ["Restaurant", "Grocery Store", "Supermarket", "Hotel", "Bakery", "Catering Service"]
receiver_types = ["NGO", "Community Center", "Individual", "Orphanage", "Old Age Home", "Shelter"]
food_names = ["Rice", "Dal", "Bread", "Vegetables", "Fruits", "Pulses", "Milk", "Eggs", "Roti", "Biryani",
              "Pasta", "Sandwiches", "Soup", "Salad", "Idli", "Dosa", "Poha", "Upma", "Khichdi", "Paneer Curry"]
food_types = ["Vegetarian", "Non-Vegetarian", "Vegan"]
meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks"]
statuses = ["Pending", "Completed", "Cancelled"]

provider_names = [
    "Annapurna Restaurant", "Fresh Mart", "City Supermarket", "Grand Hotel", "Sweet Bakery",
    "Tasty Bites", "Green Grocers", "Metro Store", "Royal Kitchen", "Spice Garden",
    "Food Junction", "Big Bazaar", "Heritage Hotel", "Mom's Kitchen", "Urban Deli",
    "Sunrise Bakery", "Paradise Restaurant", "Daily Fresh", "The Food Hub", "Nourish Store"
]

receiver_names = [
    "Hope NGO", "City Community Center", "Aarav Kumar", "Sunshine Orphanage", "Golden Years Home",
    "Safe Harbor Shelter", "Seva Trust", "People First NGO", "United Community", "New Life Center",
    "Helping Hands", "Bright Future NGO", "Janata Community", "Care for All", "Relief Foundation",
    "Street Angels", "Share & Care", "Food for All NGO", "Prayas NGO", "Asha Community"
]

# ── Providers ──────────────────────────────────────────────────────────────────
with open("/home/claude/food_wastage_project/providers_data.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Provider_ID", "Name", "Type", "Address", "City", "Contact"])
    for i in range(1, 51):
        w.writerow([
            i,
            provider_names[(i - 1) % len(provider_names)] + (f" {i}" if i > len(provider_names) else ""),
            random.choice(provider_types),
            f"{random.randint(1, 999)} {random.choice(['MG Road', 'Main Street', 'Park Avenue', 'Gandhi Nagar', 'Station Road'])}",
            random.choice(cities),
            f"9{random.randint(100000000, 999999999)}"
        ])

# ── Receivers ──────────────────────────────────────────────────────────────────
with open("/home/claude/food_wastage_project/receivers_data.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Receiver_ID", "Name", "Type", "City", "Contact"])
    for i in range(1, 41):
        w.writerow([
            i,
            receiver_names[(i - 1) % len(receiver_names)] + (f" {i}" if i > len(receiver_names) else ""),
            random.choice(receiver_types),
            random.choice(cities),
            f"8{random.randint(100000000, 999999999)}"
        ])

# ── Food Listings ──────────────────────────────────────────────────────────────
base_date = datetime(2024, 1, 1)
with open("/home/claude/food_wastage_project/food_listings_data.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Food_ID", "Food_Name", "Quantity", "Expiry_Date", "Provider_ID", "Provider_Type", "Location", "Food_Type", "Meal_Type"])
    for i in range(1, 201):
        expiry = base_date + timedelta(days=random.randint(1, 30))
        pid = random.randint(1, 50)
        w.writerow([
            i,
            random.choice(food_names),
            random.randint(5, 200),
            expiry.strftime("%Y-%m-%d"),
            pid,
            random.choice(provider_types),
            random.choice(cities),
            random.choice(food_types),
            random.choice(meal_types)
        ])

# ── Claims ─────────────────────────────────────────────────────────────────────
with open("/home/claude/food_wastage_project/claims_data.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Claim_ID", "Food_ID", "Receiver_ID", "Status", "Timestamp"])
    for i in range(1, 151):
        ts = base_date + timedelta(days=random.randint(0, 60), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        w.writerow([
            i,
            random.randint(1, 200),
            random.randint(1, 40),
            random.choice(statuses),
            ts.strftime("%Y-%m-%d %H:%M:%S")
        ])

print("✅ All 4 CSV datasets generated successfully!")
