"""
This module contains test cases for the booking functionalities
of the FastAPI application. It uses pytest for testing and provides helper 
functions to create test data in the database.

Test Cases:
- test_book_success: Tests successful booking of an inventory item by a member.
- test_book_max_reached: Tests booking failure when a member has reached the maximum number of active bookings.
- test_book_no_remaining: Tests booking failure when the inventory item has no remaining count.
- test_book_expired_item: Tests booking failure when the inventory item is expired.
- test_cancel_success: Tests successful cancellation of a booking and updates the member's booking count and inventory's remaining count.
- test_cancel_not_found_or_inactive: Tests cancellation failure when the booking reference does not exist or is already inactive.

Fixtures:
- db_session: Provides a SQLAlchemy session for tests and ensures teardown after each test.

Helper Functions:
- create_member: Creates a Member in the database for testing.
- create_inventory: Creates an Inventory item in the database for testing.

Assertions:
- Verify the response status code and data for each test case.
- Verify the database records are updated correctly after booking and cancellation.

"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.DB.database import SessionLocal
from app.DB.models import Member, Inventory, Booking
from app.config import API_KEY 

# load the secret key from environment variables
# or use a default value for testing


client = TestClient(app)

@pytest.fixture
def db_session():
    """
    Provide a SQLAlchemy session for tests.
    Make sure to tear down after each test.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_member(db_session, name="John", surname="Doe", booking_count=0, date_joined=None):
    """
    Helper function to create a Member in the DB.
    """
    if not date_joined:
        date_joined = datetime(2024, 1, 1, 10, 0, 0)
    member = Member(
        name=name, 
        surname=surname, 
        booking_count=booking_count, 
        date_joined=date_joined
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)
    return member

def create_inventory(db_session, title="TestItem", remaining_count=1, expiration_date=None):
    """
    Helper function to create an Inventory item in the DB.
    """
    if not expiration_date:
        # default to a far future date
        expiration_date = datetime(2030, 12, 31).date()
    inventory = Inventory(
        title=title, 
        description="Some Desc", 
        remaining_count=remaining_count, 
        expiration_date=expiration_date
    )
    db_session.add(inventory)
    db_session.commit()
    db_session.refresh(inventory)
    return inventory

def test_book_success(db_session):
    member = create_member(db_session, booking_count=0)
    inv = create_inventory(db_session, remaining_count=1)

    response = client.post(
        "/api/book",
        headers={"x-api-key": API_KEY},  # if using auth
        json={
            "member_id": member.id,
            "inventory_id": inv.id
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["member_id"] == member.id
    assert data["inventory_id"] == inv.id
    assert data["is_active"] == True

    db_session.refresh(member)
    db_session.refresh(inv)
    assert member.booking_count == 1
    assert inv.remaining_count == 0

def test_book_max_reached(db_session):
    member = create_member(db_session, booking_count=0)
    inv = create_inventory(db_session, remaining_count=5)

    # Creating 2 active bookings in the DB
    booking1 = Booking(member_id=member.id, inventory_id=inv.id, is_active=True)
    booking2 = Booking(member_id=member.id, inventory_id=inv.id, is_active=True)
    db_session.add_all([booking1, booking2])
    db_session.commit()

    # Now the DB actually has 2 active bookings for that member
    # Attempt to book again
    response = client.post(
        "/api/book",
        headers={"x-api-key": API_KEY},
        json={
            "member_id": member.id,
            "inventory_id": inv.id
        }
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert "Member has reached the maximum" in data["detail"]

def test_book_no_remaining(db_session):
    """
    If remaining_count == 0, booking should fail with 400.
    """
    member = create_member(db_session, booking_count=0)
    inv = create_inventory(db_session, remaining_count=0)  # out of stock

    response = client.post(
        "/api/book",
        headers={"x-api-key": API_KEY},
        json={
            "member_id": member.id,
            "inventory_id": inv.id
        }
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert "No remaining count" in data["detail"]

def test_book_expired_item(db_session):
    """
    If inventory item is expired, should fail with 400 (if your code checks expiration).
    """
    member = create_member(db_session)
    # Set an expiration date in the past
    inv = create_inventory(db_session, expiration_date=datetime(2020, 1, 1).date())

    response = client.post(
        "/api/book",
        headers={"x-api-key": API_KEY},
        json={
            "member_id": member.id,
            "inventory_id": inv.id
        }
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert "Inventory item is expired" in data["detail"]

def test_cancel_success(db_session):
    """
    Create a booking, then cancel it. 
    Check that is_active becomes False, member.booking_count decrements, inventory.remaining_count increments.
    """
    member = create_member(db_session, booking_count=0)
    inv = create_inventory(db_session, remaining_count=1)

    # Book it
    book_res = client.post(
        "/api/book",
        headers={"x-api-key": API_KEY},
        json={
            "member_id": member.id,
            "inventory_id": inv.id
        }
    )
    assert book_res.status_code == 200, book_res.text
    booking_data = book_res.json()
    ref = booking_data["booking_reference"]

    # Cancel it
    cancel_res = client.post(
        "/api/cancel",
        headers={"x-api-key": API_KEY},
        params={"booking_reference": ref}  # or use a JSON body, depending on your endpoint
    )
    assert cancel_res.status_code == 200, cancel_res.text
    cancel_data = cancel_res.json()
    assert cancel_data["is_active"] == False

    db_session.refresh(member)
    db_session.refresh(inv)
    assert member.booking_count == 0
    assert inv.remaining_count == 1

def test_cancel_not_found_or_inactive(db_session):
    """
    If the booking doesn't exist or is already inactive, we expect a 404.
    """
    # Attempt to cancel a reference that doesn't exist
    response = client.post(
        "/api/cancel",
        headers={"x-api-key": API_KEY},
        params={"booking_reference": "FAKE-REF"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Active booking with this reference not found" in data["detail"]

    # Create a booking, then mark it inactive in the DB
    member = create_member(db_session, booking_count=1)
    inv = create_inventory(db_session, remaining_count=0)
    booking = Booking(
        member_id=member.id,
        inventory_id=inv.id,
        is_active=False  # already canceled in DB
    )
    db_session.add(booking)
    db_session.commit()
    ref = booking.booking_reference  # auto-generated if you have a default generator

    # Attempt to cancel an already inactive booking
    response2 = client.post(
        "/api/cancel",
        headers={"x-api-key": API_KEY},
        params={"booking_reference": ref}
    )
    assert response2.status_code == 404
    data2 = response2.json()
    assert "Active booking with this reference not found" in data2["detail"]
