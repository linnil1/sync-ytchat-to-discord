import logging
from env import DISCORD_TOKEN

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)
