import csv
import io
import re

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Invitee


def normalize_phone(phone):

    phone = phone.strip()

    return re.sub(
        r"[\s\-\(\)]",
        "",
        phone
    )


def is_valid_phone(phone):

    return bool(
        re.fullmatch(
            r"\+?[0-9]{10,15}",
            phone
        )
    )


def is_valid_email(email):

    try:

        validate_email(email)

        return True

    except ValidationError:

        return False


def import_invitees_from_csv(uploaded_file):

    try:

        decoded_file = uploaded_file.read().decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError:

        return {
            "success": False,
            "message": (
                "Unable to read CSV. "
                "Please upload a UTF-8 encoded CSV file."
            )
        }


    csv_data = io.StringIO(
        decoded_file
    )

    reader = csv.DictReader(
        csv_data
    )


    if not reader.fieldnames:

        return {
            "success": False,
            "message": "CSV file is empty or invalid."
        }


    headers = {
        header.strip().lower()
        for header in reader.fieldnames
        if header
    }


    required_columns = {
        "name",
        "phone",
        "email"
    }


    missing_columns = (
        required_columns
        - headers
    )


    if missing_columns:

        return {
            "success": False,
            "message": (
                "Missing required columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )
        }


    existing_phones = set(
        Invitee.objects.values_list(
            "phone",
            flat=True
        )
    )


    seen_phones = set()

    new_invitees = []

    errors = []

    duplicate_count = 0


    for row_number, row in enumerate(
        reader,
        start=2
    ):

        name = (
            row.get("name") or ""
        ).strip()


        phone = normalize_phone(
            row.get("phone") or ""
        )


        email = (
            row.get("email") or ""
        ).strip().lower()


        if not name:

            errors.append({
                "row": row_number,
                "error": "Name is required."
            })

            continue


        if not phone:

            errors.append({
                "row": row_number,
                "error": "Phone is required."
            })

            continue


        if not is_valid_phone(phone):

            errors.append({
                "row": row_number,
                "error": "Invalid phone number."
            })

            continue


        if not email:

            errors.append({
                "row": row_number,
                "error": "Email is required."
            })

            continue


        if not is_valid_email(email):

            errors.append({
                "row": row_number,
                "error": "Invalid email address."
            })

            continue


        if (
            phone in existing_phones
            or phone in seen_phones
        ):

            duplicate_count += 1

            continue


        seen_phones.add(
            phone
        )


        new_invitees.append(

            Invitee(
                name=name,
                phone=phone,
                email=email
            )

        )


    Invitee.objects.bulk_create(
        new_invitees,
        batch_size=1000
    )


    return {
        "success": True,
        "created": len(new_invitees),
        "duplicates": duplicate_count,
        "errors": errors
    }