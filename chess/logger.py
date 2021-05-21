# coding=utf-8

import sys
import logging

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='[%(created)d] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',)
logger = logging.getLogger()

logger.info("init logging...")
