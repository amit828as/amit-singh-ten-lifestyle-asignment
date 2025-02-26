"""
CLI entry point for operations such as CSV uploads.
"""
import argparse
import csv
from datetime import datetime
from typing import Optional

from app.database import SessionLocal
from app.models import Member, Inventory

from datetime import datetime

def upload_csv(file_path: str):
    """
    Uploads a CSV file into the database.
    Detects if it's a members.csv or inventory.csv by the column headers.
    """
    db = SessionLocal()
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

            if not headers:
                print(f"Empty or invalid CSV: {file_path}")
                return

            if "name" in headers and "surname" in headers:
                # We assume this is a Member CSV
                upload_members(reader, db)
            elif "title" in headers and "description" in headers:
                # We assume this is an Inventory CSV
                upload_inventory(reader, db)
            else:
                print("Unsupported CSV structure. Could not identify columns.")
    finally:
        db.close()


def upload_members(reader: csv.DictReader, db):
    """
    Inserts Member rows from CSV data into the DB.
    CSV columns expected: name, surname, booking_count, date_joined
    """
    for row in reader:
        raw_date = row.get("date_joined", "").strip()
        joined_datetime = parse_date_joined(raw_date)
        if not joined_datetime:
            print(f"Skipping row due to invalid date_joined format: {raw_date}")
            continue

        booking_count_str = row.get("booking_count", "0")
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

    db.commit()
    print("Members CSV imported successfully.")


def parse_date_joined(raw_date: str):
    """
    Try to parse the date_joined field in either
    'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS' format.
    """
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(raw_date, fmt)
        except ValueError:
            continue
    return None



def upload_inventory(reader: csv.DictReader, db):
    """
    Inserts Inventory rows from CSV data into the DB.
    CSV columns expected: title, description, remaining_count, expiration_date
    """
    for row in reader:
        # Convert expiration_date from "DD/MM/YYYY"
        raw_date = row.get("expiration_date", "")
        try:
            expire_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
        except ValueError:
            print(f"Skipping row due to invalid expiration_date format: {raw_date}")
            continue

        remaining_count_str = row.get("remaining_count", "0")
        try:
            remaining_count = int(remaining_count_str)
        except ValueError:
            remaining_count = 0

        inventory_item = Inventory(
            title=row.get("title", "").strip(),
            description=row.get("description", "").strip(),
            remaining_count=remaining_count,
            expiration_date=expire_date
        )
        db.add(inventory_item)
    db.commit()
    print("Inventory CSV imported successfully.")


def main():
    """
    Parse CLI arguments and dispatch commands.
    """
    parser = argparse.ArgumentParser(description="CLI for uploading CSV files to the booking system.")
    parser.add_argument(
        "--upload-file", 
        type=str, 
        help="Path to the CSV file (members.csv or inventory.csv)."
    )

    args = parser.parse_args()

    if args.upload_file:
        upload_csv(args.upload_file)


if __name__ == "__main__":
    main()
