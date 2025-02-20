import logging
from logging.handlers import RotatingFileHandler
import os

def start_logger():
    """
    Configures and starts the logging system with both console and file handlers.
    Logs will include: timestamp, logger name, log level, and the message. 
    Logs will be written to the console and to a rotating file handler with a 
    maximum size and 1 backup.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_directory = os.path.join(base_dir, "logs")

    file_handler = RotatingFileHandler(
        filename=os.path.join(log_directory, "app.log"),
        maxBytes=1 * 1024 * 1024,  # 5 MB per file
        backupCount=1,             # Keep 3 backups
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    log_level = logging.DEBUG

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
