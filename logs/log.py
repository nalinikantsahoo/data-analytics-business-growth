import logging
from datetime import datetime

import colorlog
import os

def setup_logger():
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Generate log filenames based on the current date
    date_str = datetime.now().strftime('%Y-%m-%d')
    full_log_file = os.path.join(log_dir, f'data_interpreter_full_log_{date_str}.log')
    error_log_file = os.path.join(log_dir, f'data_interpreter_error_log_{date_str}.log')

    # Create a custom logger
    logger = logging.getLogger('data_interpreter_logger')
    logger.setLevel(logging.DEBUG)  # Set the logger to capture all levels

    # Create handlers for both full logs and error logs
    full_log_handler = logging.FileHandler(full_log_file)
    full_log_handler.setLevel(logging.DEBUG)  # Capture all logs

    error_log_handler = logging.FileHandler(error_log_file)
    error_log_handler.setLevel(logging.ERROR)  # Capture only error and critical logs

    # Create formatters and add them to the handlers
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    full_log_handler.setFormatter(log_format)
    error_log_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(full_log_handler)
    logger.addHandler(error_log_handler)

    # Add color logging for console
    color_format = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # Console handler with color
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Log only INFO and above to console
    console_handler.setFormatter(color_format)
    logger.addHandler(console_handler)

    return logger
