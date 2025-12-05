import logging


def get_logger(name: str) -> logging.Logger:
    """
    Provide a basic logger configured for console output.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# git remote set-url origin https://github.com/entangleX/ai-insta-meme-automation.git
