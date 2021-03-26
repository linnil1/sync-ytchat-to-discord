import logging
import argparse
from env import DISCORD_TOKEN


def setup_logger():
    logger = logging.getLogger("sync-ytchat")
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    return logger


def setup_parser():
    parser = argparse.ArgumentParser(description="Sync YTchat to Discord",
                                     usage=".synchat {start,stop} [id]")
    parser.add_argument('method', choices=["start", "stop"])
    parser.add_argument('id', nargs="?", help="youtube_video_id")
    return parser


logger = setup_logger()
