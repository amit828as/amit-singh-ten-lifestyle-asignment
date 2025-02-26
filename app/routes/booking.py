"""
This module defines the API routes for managing bookings using FastAPI.
It includes endpoints for creating and canceling bookings, ensuring that
all operations adhere to specified constraints.

Routes:
- POST /book: Create a new booking if constraints are met.

Dependencies:
- FastAPI's APIRouter for defining routes.
- SQLAlchemy's Session for database interactions.
- HTTPException and status for handling HTTP errors.
- datetime for date and time operations.

Models:
- Member: Represents a member in the system.
- Inventory: Represents an inventory item available for booking.
- Booking: Represents a booking made by a member for an inventory item.

Schemas:
- BookingCreate: Schema for validating booking creation data.
- BookingRead: Schema for returning booking details.

Constraints:
- A member can have a maximum of 2 active bookings.
- An inventory item must have a remaining count greater than 0.
- An inventory item must not be expired.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Member, Inventory, Booking
from app.schemas import BookingCreate, BookingRead

router = APIRouter()

@router.post("/book", response_model=BookingRead)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new booking if constraints are satisfied:
    - Member has fewer than 2 active bookings
    - Inventory has remaining_count > 0
    """
    # Fetch the Member & Inventory
    member = db.query(Member).filter(Member.id == booking_data.member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id={booking_data.member_id} not found."
        )

    inventory_item = db.query(Inventory).filter(Inventory.id == booking_data.inventory_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with id={booking_data.inventory_id} not found."
        )

    # Check constraints
    # Member has < 2 active bookings
    active_bookings_count = db.query(Booking).filter(
        Booking.member_id == member.id,
        Booking.is_active == True
    ).count()

    if active_bookings_count >= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member has reached the maximum of 2 active bookings."
        )

    # Inventory has remaining_count > 0
    if inventory_item.remaining_count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No remaining count for this inventory item."
        )

    # Check if inventory is expired
    # If today's date is past expiration_date, reject the booking
    if inventory_item.expiration_date < datetime.utcnow().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory item is expired; cannot be booked."
        )

    # Create the Booking
    booking = Booking(
        member_id=member.id,
        inventory_id=inventory_item.id,
        # is_active=True by default (set in models)
        # booking_reference is auto-generated (UUID in models)
    )
    db.add(booking)

    # Decrement the inventory count
    inventory_item.remaining_count -= 1

    # Increment the member booking_count
    member.booking_count += 1

    db.commit()
    db.refresh(booking)  # refresh to get the booking_reference, id, etc.

    return booking
