import logging
from colorama import Fore, Style

# Define custom log levels with colors
class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""
    def format(self, record):
        level_colors = {
            logging.DEBUG: Fore.CYAN,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA,
        }
        color = level_colors.get(record.levelno, Fore.WHITE)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

# Configure logging
def setup_logger(name=None, level=logging.DEBUG):
    """Setup logger with colored output."""
    # Create logger
    logger = logging.getLogger(name if name else __name__)
    logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Set custom formatter with colors
    formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger