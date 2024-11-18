"""
This is the main file of the application. It starts the application
by calling the start_window function from the main_screen module.
"""

from Modules.main_screen import start_window
from Modules.logger import create_logger

if __name__ == "__main__":
    logger = create_logger()
    logger.info("Starting application...")
    start_window()
