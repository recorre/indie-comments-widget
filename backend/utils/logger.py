# backend/utils/logger.py
# This module provides logging utilities for the backend.

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger instance.
    """
    # Placeholder implementation
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_info(logger: logging.Logger, message: str):
    """
    Log an info message.

    Args:
        logger (logging.Logger): The logger instance.
        message (str): The message to log.
    """
    logger.info(message)


def log_error(logger: logging.Logger, message: str):
    """
    Log an error message.

    Args:
        logger (logging.Logger): The logger instance.
        message (str): The message to log.
    """
    logger.error(message)