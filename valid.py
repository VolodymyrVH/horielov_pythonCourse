import re
import logging
from datetime import datetime


def validate_user_full_name(full_name):
    cleaned = re.sub(r'[^a-zA-Z\s]', '', full_name)
    parts = cleaned.strip().split()
    if len(parts) != 2:
        logging.error(f"Invalid full name format: {full_name}")
        raise ValueError("Full name must contain exactly one name and one surname")
    logging.info(f"Validated full name: {full_name} -> {parts[0]} {parts[1]}")
    return parts[0], parts[1]


def validate_restricted_field(field_name, value, allowed_values):
    if value not in allowed_values:
        logging.error(f"Invalid value {value} for field {field_name}")
        raise ValueError(f"Not allowed value {value} for field {field_name}!")
    return value


def validate_datetime(datetime_str):
    if not datetime_str:
        result = datetime.now().isoformat()
        logging.info(f"No datetime provided, using current time: {result}")
        return result
    if not isinstance(datetime_str, str):
        logging.error(f"Invalid datetime format: {datetime_str}")
        raise ValueError("Datetime must be a string")
    return datetime_str


def validate_account_number(account_number):
    cleaned = re.sub(r'[#%_?&]', '-', account_number)

    if len(cleaned) != 18:
        logging.error(f"Invalid account number length: {len(cleaned)}")
        raise ValueError(f"Account number must be 18 characters, got {len(cleaned)}!")

    if not cleaned.startswith('ID--'):
        logging.error(f"Account number does not start with 'ID--': {cleaned}")
        raise ValueError("Account number must start with 'ID--'!")

    pattern = r'[a-zA-Z]{1,3}-[0-9]+-'
    if not re.search(pattern, cleaned):
        logging.error(f"Account number missing required pattern: {cleaned}")
        raise ValueError("Account number must contain pattern: 1-3 letters, dash, 1+ digits, dash!")

    logging.info(f"Validated account number: {cleaned}")
    return cleaned