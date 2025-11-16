import logging
from .config import settings

def setup_logging():
    """Konfiguruje logování pro aplikaci."""
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    # Vytvoření root loggeru
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Formátování
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler pro konzoli
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler pro soubor (pokud je nastaven)
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Potlačení příliš podrobných logů z některých knihoven
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)