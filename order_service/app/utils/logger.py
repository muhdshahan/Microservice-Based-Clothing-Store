import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("order_service.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("order_service")
