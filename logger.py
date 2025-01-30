import logging

def setup_logger():
    """Returns created logger"""
    # Get or create logger
    logger = logging.getLogger("logger")

    # Only add handlers if the logger doesn't have any
    if not logger.handlers:
        # Minimum level of messages to capture
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler("log.log", "w")
        file_handler.setLevel(logging.DEBUG)

        # Console handler to show logs in terminal
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Format for log messages
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add both handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
