# backend/utils/hash.py
# This module provides hashing utilities for the backend.

import hashlib


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    # Placeholder implementation
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password (str): The plain text password.
        hashed (str): The hashed password.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    # Placeholder implementation
    return hash_password(password) == hashed