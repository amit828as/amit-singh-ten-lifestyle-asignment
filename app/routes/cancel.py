from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter()

@router.delete("/cancel/{booking_id}", response_model=schemas.Booking)
def cancel_booking(booking_id: int, db: Session = Depends(database.SessionLocal)):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.delete(db_booking)
    db.commit()
    return db_booking
