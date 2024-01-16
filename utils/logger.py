import logging
import inspect

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors to the levelname and include function name"""

    grey = "\x1b[38;21m"
    blue = "\x1b[34m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    reset = "\x1b[0m"

    LEVEL_COLORS = {
        logging.DEBUG: blue,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: red
    }

    def format(self, record):
        # Dynamically find the name of the calling function
        stack = inspect.stack()
        func_name = "unknown"
        for frame in stack:
            if frame.function not in ["emit", "format"] and 'logging' not in frame.filename:
                func_name = frame.function
                break
        record.func_name = func_name

        # Colorize levelname
        color = self.LEVEL_COLORS.get(record.levelno, self.grey)
        record.levelname = color + record.levelname + self.reset

        # Set the format and return the formatted record
        self._style._fmt = "%(levelname)s: [%(func_name)s] %(asctime)s - %(message)s"
        return super(CustomFormatter, self).format(record)