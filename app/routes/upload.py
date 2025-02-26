"""
This module defines API endpoints for uploading CSV files containing members and inventory data.
It includes two endpoints:
1. /members: Uploads a CSV file of members with columns: name, surname, booking_count, date_joined.
2. /inventory: Uploads a CSV file of inventory items with columns: title, description, remaining_count, expiration_date.

Functions:
- upload_members_file: Endpoint to handle the upload of members CSV file.
- upload_inventory_file: Endpoint to handle the upload of inventory items CSV file.
- parse_member_date: Helper function to parse member date strings.
- parse_inventory_date: Helper function to parse inventory date strings.

Dependencies:
- FastAPI for routing and HTTP exception handling.
- SQLAlchemy ORM for database interactions.
- Session dependency for database session management.

Constraints:
- Date formats must be in 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS' for members
- Date format must be in 'DD/MM/YYYY' for inventory items

"""

import csv
from io import StringIO
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.DB.database import get_db
from app.DB.models import Member, Inventory
from app.security.auth import api_key_auth

router = APIRouter()

@router.post("/members", status_code=status.HTTP_201_CREATED, dependencies=[Depends(api_key_auth)])
def upload_members_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint to upload a CSV of members.
    Expected columns: name, surname, booking_count, date_joined
    """
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(contents))
    rows_processed = 0

    for row in reader:
        raw_date = row.get("date_joined", "").strip()
        joined_datetime = parse_member_date(raw_date)  # We'll define this helper below.
        if not joined_datetime:
            # skip invalid date formats
            continue

        booking_count_str = row.get("booking_count", "0").strip()
        try:
            booking_count = int(booking_count_str)
        except ValueError:
            booking_count = 0

        member = Member(
            name=row.get("name", "").strip(),
            surname=row.get("surname", "").strip(),
            booking_count=booking_count,
            date_joined=joined_datetime
        )
        db.add(member)
        rows_processed += 1

    db.commit()
    return {"message": f"Uploaded {rows_processed} members."}


@router.post("/inventory", status_code=status.HTTP_201_CREATED, dependencies=[Depends(api_key_auth)])
def upload_inventory_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint to upload a CSV of inventory items.
    Expected columns: title, description, remaining_count, expiration_date
    """
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(contents))
    rows_processed = 0

    for row in reader:
        raw_exp = row.get("expiration_date", "").strip()
        expiration_date = parse_inventory_date(raw_exp)
        if not expiration_date:
            continue

        try:
            remaining = int(row.get("remaining_count", "0").strip())
        except ValueError:
            remaining = 0

        item = Inventory(
            title=row.get("title", "").strip(),
            description=row.get("description", "").strip(),
            remaining_count=remaining,
            expiration_date=expiration_date
        )
        db.add(item)
        rows_processed += 1

    db.commit()
    return {"message": f"Uploaded {rows_processed} inventory items."}


def parse_member_date(raw: str):
    """
    Try to parse a date in 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS'.
    Return None if fails.
    """
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    return None

def parse_inventory_date(raw: str):
    """
    Try to parse a date in 'DD/MM/YYYY'.
    Return None if fails.
    """
    from datetime import datetime
    try:
        return datetime.strptime(raw, "%d/%m/%Y").date()
    except ValueError:
        return None
