"""
ChatterFix Backend - Synthetic Data Generation
This module generates realistic-looking sample data for demonstration and testing.
"""

import random
from faker import Faker
from datetime import datetime, timedelta
from . import models, database, work_orders, assets, parts, accounting, auth

# Initialize Faker for data generation
fake = Faker()

def clear_all_data():
    """
    Deletes all documents from all known collections.
    USE WITH EXTREME CAUTION.
    """
    print("🔥 Deleting all existing data...")
    collections = [
        "users", "work_orders", "assets", "parts", "transactions"
    ]
    for collection in collections:
        database.delete_collection(collection)
    print("✅ All collections cleared.")

def generate_synthetic_data(num_users=5, num_assets=20, num_parts=50, num_work_orders=100):
    """
    Generates a complete set of synthetic data and populates the database.
    This is an idempotent operation if run after clearing data.
    """
    print("🌱 Starting synthetic data generation...")

    # 1. Clear existing data to ensure a fresh start
    clear_all_data()

    # 2. Create Users
    print("👤 Creating users...")
    user_ids = []
    # Ensure at least one of each role
    roles = ['admin', 'manager', 'technician']
    for i in range(num_users):
        username = fake.user_name()
        email = fake.email()
        # Assign roles, ensuring we have at least one of each
        role = roles[i] if i < len(roles) else random.choice(roles)
        password = "password123" # Use a standard password for demo data
        try:
            user_id = auth.create_user(username, password, role, email)
            user_ids.append(user_id)
            print(f" -> Created user: {username} ({role})")
        except ValueError as e:
            print(f"⚠️ Could not create user {username}: {e}")
    
    # Get all users again to ensure we have the full list
    all_users = auth.get_all_users()
    technician_ids = [u.id for u in all_users if u.role == 'technician']


    # 3. Create Assets
    print("🏭 Creating assets...")
    asset_ids = []
    asset_types = ['HVAC Unit', 'Forklift', 'Conveyor Belt', 'CNC Machine', 'Industrial Freezer']
    for _ in range(num_assets):
        try:
            asset_id = assets.add_asset(
                name=f"{random.choice(asset_types)} - {fake.word().capitalize()}{random.randint(100, 999)}",
                asset_type=random.choice(asset_types),
                location=f"Building {random.randint(1, 5)} - Floor {random.randint(1, 3)}",
                purchase_date=fake.date_this_decade().strftime('%Y-%m-%d'),
                purchase_price=round(random.uniform(5000, 50000), 2),
                serial_number=fake.ean(length=13),
                status='active'
            )
            asset_ids.append(asset_id)
        except Exception as e:
            print(f"Error creating asset: {e}")
    print(f" -> Created {len(asset_ids)} assets.")


    # 4. Create Parts
    print("🔩 Creating parts...")
    part_ids = []
    part_names = ['Filter', 'Bearing', 'Motor', 'Sensor', 'Gasket', 'Valve']
    for _ in range(num_parts):
        try:
            part_id = parts.add_part(
                name=f"{random.choice(part_names)} - Model {fake.bothify(text='??-####').upper()}",
                part_number=fake.ean(length=8),
                stock_quantity=random.randint(5, 100),
                location=f"Warehouse A - Shelf {random.randint(1, 20)}"
            )
            part_ids.append(part_id)
        except Exception as e:
            print(f"Error creating part: {e}")
    print(f" -> Created {len(part_ids)} parts.")


    # 5. Create Work Orders (Historical and Current)
    print("📝 Creating work orders...")
    wo_statuses = ['open', 'in_progress', 'on_hold', 'completed', 'cancelled']
    wo_priorities = ['low', 'medium', 'high', 'critical']
    wo_titles = ["Routine Inspection", "Emergency Repair", "Component Replacement", "System Calibration"]
    for i in range(num_work_orders):
        try:
            # Make most work orders completed to train the predictive model
            status = 'completed' if i < (num_work_orders * 0.8) else random.choice(wo_statuses)
            
            # Create the work order
            wo_id = work_orders.create_work_order(
                title=random.choice(wo_titles),
                description=fake.sentence(),
                priority=random.choice(wo_priorities),
                equipment_id=random.choice(asset_ids) if asset_ids else "",
                status=status
            )

            # Assign and add history to non-open/suggested work orders
            if status != 'open' and status != 'suggested' and technician_ids:
                assigned_user = random.choice(all_users)
                update_data = {'assigned_to_id': assigned_user.id}
                
                # Simulate creation and completion dates
                created_date = datetime.utcnow() - timedelta(days=random.randint(1, 730))
                update_data['created_at'] = created_date
                
                if status in ['completed', 'cancelled']:
                    completion_date = created_date + timedelta(days=random.randint(1, 5))
                    update_data['completed_at'] = completion_date
                    update_data['completion_notes'] = fake.paragraph()

                database.update_document("work_orders", wo_id, update_data)

        except Exception as e:
            print(f"Error creating work order: {e}")
    print(f" -> Created {num_work_orders} work orders.")

    print("✅ Synthetic data generation complete!")
    return True
