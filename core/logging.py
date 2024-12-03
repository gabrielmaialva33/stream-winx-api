import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.log", maxBytes=5000000, backupCount=10),
        logging.StreamHandler(),
    ],
)

logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("fastapi").setLevel(logging.ERROR)


def logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
