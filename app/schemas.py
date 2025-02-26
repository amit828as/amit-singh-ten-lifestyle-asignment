"""
Pydantic schemas for request and response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

class MemberBase(BaseModel):
    """
    Base schema for Member model.
    """
    name: str
    surname: str
    booking_count: int = 0
    date_joined: datetime

class MemberCreate(MemberBase):
    """
    Schema used when creating a new Member from CSV or API.
    """
    pass

class MemberRead(MemberBase):
    """
    Schema used for reading member data (response).
    """
    id: int

    class Config:
        from_attribute = True


class InventoryBase(BaseModel):
    """
    Base schema for Inventory model.
    """
    title: str
    description: Optional[str] = None
    remaining_count: int
    expiration_date: date

class InventoryCreate(InventoryBase):
    """
    Schema used when creating a new Inventory item (CSV or API).
    """
    pass

class InventoryRead(InventoryBase):
    """
    Schema used for reading Inventory data (response).
    """
    id: int

    class Config:
        from_attribute = True


class BookingBase(BaseModel):
    """
    Base schema for Booking model.
    """
    member_id: int
    inventory_id: int
    is_active: bool = True

class BookingCreate(BookingBase):
    """
    Schema for creating a new Booking.
    """
    pass

class BookingRead(BookingBase):
    """
    Schema for reading booking data (response).
    """
    id: int
    booking_reference: str
    booking_datetime: datetime

    class Config:
        from_attribute = True
