
import logging
import os
import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.config import LOGS_DIR

def setup_logger(name="RAG_System"):
    """
    Sets up a logger that writes to a new file in the LOGS_DIR for each run.
    """
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"run_{timestamp}.log"
    log_file_path = os.path.join(LOGS_DIR, log_filename)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # File Handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Keep console clean, only INFO+
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # Avoid adding handlers multiple times if logger is reused
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Writing to {log_file_path}")
    return logger, log_file_path
