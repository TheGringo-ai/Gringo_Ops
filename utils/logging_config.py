import logging
import json
import sys

class JsonFormatter(logging.Formatter):
    """
    Formats log records as a JSON string.
    """
    def format(self, record):
        """Placeholder docstring for format."""
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging(log_level=logging.INFO):
    """
    Configures logging to output structured JSON logs to stdout.
    This is ideal for services running in containers like Cloud Run.
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create a new handler that streams to stdout
    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# Example usage:
if __name__ == '__main__':
    logger = setup_logging()
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.error("An exception occurred", exc_info=True)
