import logging
import sys
from pathlib import Path



def setup_logging(project_root):
    log_file = Path(project_root).resolve() / "logs" / "execution.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("bearing_fault_detection")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Prevent duplicate messages when rerunning notebook setup.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(
        log_file, mode="a", encoding="utf-8"
    )

    for handler, level in [(console, logging.INFO), (file_handler, logging.DEBUG)]:
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.info("Logging started | file=%s", log_file)
    return logger


#from pathlib import Path
#import sys

#project = Path(r"C:\Users\redhu\OneDrive\Desktop\Bearing_fault_detection")
#sys.path.insert(0, str(project))

#from logging_config import setup_logging

#logger = setup_logging(project)
#logger.info("Console and file logging are ready")