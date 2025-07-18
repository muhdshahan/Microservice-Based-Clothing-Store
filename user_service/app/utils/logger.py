import logging
import os

# Ensure the logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file_path = os.path.join(log_dir, "user_service.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # capture info, warning, error, critical
    format="%(asctime)s [%(levelname)s] %(message)s",  # structured log format
    handlers=[
        logging.FileHandler(log_file_path),  # logs to file
        logging.StreamHandler()              # logs to console
    ]
)

# Create or get a logger named "user_service"
logger = logging.getLogger("user_service")
