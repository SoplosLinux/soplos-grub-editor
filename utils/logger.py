"""
Logging utility for Soplos Grub Editor.
"""

import sys
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('soplos-grub-editor')

def log_info(message: str):
    logger.info(message)

def log_warning(message: str):
    logger.warning(message)

def log_error(message: str, error: Exception = None):
    if error:
        logger.error(f"{message}: {error}")
    else:
        logger.error(message)

def log_debug(message: str):
    logger.debug(message)
