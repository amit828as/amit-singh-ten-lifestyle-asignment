"""
SQLAlchemy models for the application.
"""
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid() -> str:
    """
    Generate a UUID string to use as a booking reference or primary key.
    """
    return str(uuid.uuid4())

class Member(Base):
    """
    Represents a member/user in the system.
    """
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    # This 'booking_count' field will be updated when we book or cancel.
    booking_count = Column(Integer, default=0, nullable=False)
    date_joined = Column(DateTime, nullable=False)

    # Relationship to the bookings (one member can have many bookings).
    bookings = relationship("Booking", back_populates="member", cascade="all, delete-orphan")

class Inventory(Base):
    """
    Represents an item (experience) that can be booked.
    """
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    remaining_count = Column(Integer, default=0, nullable=False)
    expiration_date = Column(Date, nullable=False)

    # Relationship to the bookings (one inventory item can have many bookings).
    bookings = relationship("Booking", back_populates="inventory", cascade="all, delete-orphan")

class Booking(Base):
    """
    Represents an actual booking record tying a Member to an Inventory item.
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Alternatively, you can store the reference in the same PK or as a separate column:
    booking_reference = Column(String(36), default=generate_uuid, unique=True, nullable=False)

    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)

    booking_datetime = Column(DateTime, default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Bidirectional relationships
    member = relationship("Member", back_populates="bookings")
    inventory = relationship("Inventory", back_populates="bookings")
