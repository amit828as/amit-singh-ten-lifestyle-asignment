from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter()

@router.post("/book", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(database.SessionLocal)):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking
