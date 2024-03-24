import logging

def configure_logging():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
