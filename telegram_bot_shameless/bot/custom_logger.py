import logging
import logging.handlers

# custom formatter for logs
class CustomFormatter(logging.Formatter):
    def format(self, record):
        user_name = getattr(record, 'user_name', '')
        user_id = getattr(record, 'user_id', '')
        log_type = record.levelname
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        message = record.getMessage()

        return f"{log_type} - {timestamp} | {user_name} (ID: {user_id}): {message}"

# settings for logs
def setup_logging():
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.INFO)

    # file for logs
    log_file = 'bot_logs.log'
    file_handler = logging.handlers.RotatingFileHandler(log_file,
                                    maxBytes=102400, backupCount=5)
    file_handler.setLevel(logging.INFO)

    # custom formatter
    formatter = CustomFormatter()
    file_handler.setFormatter(formatter)

    # add file_handler to logger
    logger.addHandler(file_handler)

    return logger
