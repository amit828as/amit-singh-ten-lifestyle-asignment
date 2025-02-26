"""
This module defines the API route for canceling a booking in the application.

The cancel_booking endpoint allows users to cancel an existing booking by providing
a booking reference. Upon cancellation, the inventory count is incremented, the member's
booking count is decremented, and the booking is marked as inactive.

Models:
- Member: Represents a member in the system.
- Inventory: Represents an inventory item available for booking.
- Booking: Represents a booking made by a member for an inventory item.

Dependencies:
- FastAPI for routing and HTTP exception handling.
- SQLAlchemy ORM for database interactions.

Routes:
- POST /cancel: Cancel an existing booking by booking reference.

Functions:
- cancel_booking: Handles the cancellation of a booking and updates the relevant
    inventory and member records in the database.

Constraints:
- The booking must be active to be canceled.
- The inventory count is incremented upon cancellation.
- The member's booking count is decremented upon cancellation.
- The booking is marked as inactive after cancellation.

"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Member, Inventory, Booking
from app.schemas import BookingRead

router = APIRouter()

@router.post("/cancel", response_model=BookingRead)
def cancel_booking(
    booking_reference: str,
    db: Session = Depends(get_db),
):
    """
    Cancel an existing booking by booking_reference.
    Increment the inventory count, decrement the member's booking count,
    and mark is_active=False.
    """
    booking = db.query(Booking).filter(
        Booking.booking_reference == booking_reference
    ).first()

    if not booking or not booking.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active booking with this reference not found."
        )

    # Mark the booking as inactive
    booking.is_active = False

    # Restore the inventory count
    inventory_item = db.query(Inventory).filter(Inventory.id == booking.inventory_id).first()
    if inventory_item:
        inventory_item.remaining_count += 1

    # Decrement the member's booking_count
    member = db.query(Member).filter(Member.id == booking.member_id).first()
    if member and member.booking_count > 0:
        member.booking_count -= 1

    db.commit()
    db.refresh(booking)
    return booking