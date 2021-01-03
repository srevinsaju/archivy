"""
Copyright (C) 2020 TheAssassin <theassassin@assassinate-you.net>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import logging
import os

import coloredlogs


def setup_logging():
    loglevel = logging.INFO
    force_colors = False

    if "DEBUG" in os.environ:
        loglevel = logging.DEBUG

    if "FORCE_COLORS" in os.environ:
        force_colors = True

    fmt = "%(asctime)s,%(msecs)03d %(name)s [%(levelname)s] %(message)s"

    # basic logging setup
    styles = coloredlogs.DEFAULT_FIELD_STYLES
    styles["pathname"] = {
        "color": "magenta",
    }
    styles["levelname"] = {
        "color": "cyan",
    }

    # configure our own loggers only
    base_logger = make_logger()
    base_logger.setLevel(loglevel)

    kwargs = dict(fmt=fmt, styles=styles, logger=base_logger)

    if force_colors:
        kwargs["isatty"] = True

    coloredlogs.install(loglevel, **kwargs)

    # hide all other loggers by default
    logging.getLogger().setLevel(logging.INFO)
    base_logger.setLevel(loglevel)

    # allow user to re-enable some loggers for debugging
    if "DEBUG_GITHUB" in os.environ:
        logging.getLogger("github").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)


def make_logger(name: str = None) -> logging.Logger:
    base_logger = logging.getLogger("archivy")

    if name is None:
        return base_logger

    return base_logger.getChild(name)
