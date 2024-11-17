""" Rich Logging """

import logging
import os
import tempfile
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Optional

from rich.logging import RichHandler


def create_logger(
    propagate: Optional[bool] = None, custom_handler: Optional[Any] = None
) -> logging.Logger:
    """
    Create a logger for use in all cases

    :param Optional[bool] propagate: Whether to propagate the logger, defaults to None
    :param Optional[Any] custom_handler: Custom handler to add to the logger, defaults to None
    :return: logger object
    :rtype: logging.Logger
    """
    loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
    rich_handler = RichHandler(rich_tracebacks=True, markup=True, show_time=False)
    file_handler = TimedRotatingFileHandler(
        filename=f"{tempfile.gettempdir()}{os.sep}RegScale.log",
        when="D",
        interval=3,
        backupCount=10,
    )

    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
        datefmt="[%Y/%m/%d %H:%M;%S]",
        handlers=(
            [rich_handler, file_handler, custom_handler]
            if custom_handler
            else [rich_handler, file_handler]
        ),
    )
    logger = logging.getLogger("rich")
    if propagate is not None:
        logger.propagate = propagate
    return logger
