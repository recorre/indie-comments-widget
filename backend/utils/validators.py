# backend/utils/validators.py
# This module provides validation utilities for the backend.

import re


def validate_email(email: str) -> bool:
    """
    Validate an email address.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    # Placeholder implementation
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """
    Validate a username.

    Args:
        username (str): The username to validate.

    Returns:
        bool: True if the username is valid, False otherwise.
    """
    # Placeholder implementation: alphanumeric and underscores, 3-20 characters
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None