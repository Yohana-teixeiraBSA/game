import logging
import logging.config
 


 
LOG_LEVEL = getattr(
    logging, str("DEBUG").upper()
)
 
if LOG_LEVEL >= logging.ERROR:
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "uvicorn": {
                "level": "ERROR",
            },
            "uvicorn.error": {
                "level": "ERROR",
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "ERROR",
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(LOGGING_CONFIG)
 
 
class ColorfulFormatter(logging.Formatter):
    """
    ColorfulFormatter class for logging
    """
 
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[91m",  # Red
    }
 
    RESET = "\033[0m"
 
    def __init__(self, app_name: str):
        super().__init__()
        self.app_name = app_name
 
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = f"{color}[{self.app_name}] {record.levelname}{self.RESET}: {record.msg}"  # noqa
        return f"{message}"
 
 
def setup_logger(app_name: str) -> logging.Logger:
    """Return a logger with the specified name."""
    log_level = getattr(
        logging, str("DEBUG").upper()
    )
    logger = logging.getLogger(app_name)
 
    logger.handlers.clear()
 
    logger.setLevel(log_level)
 
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = ColorfulFormatter(app_name=app_name)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
 
    logger.propagate = False
 
    return logger
 
 