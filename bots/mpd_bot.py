"""MPD Bot will run continuously to run background updates and health status of the mpd"""
import asyncio
import logging

from helpers.musicplayer import mpdproxy

async def main():
    """Initializes Prosolis Radio Bot for MPD."""
    log_format = '%(asctime)s %(message)s'
    log_level = 10

    logging.basicConfig(format=log_format, level=log_level)
    logger = logging.getLogger('MPDBot')
    logger.info("MPD Bot has started")

    while True:

        mpdproxy.update_play_history()

if __name__ == "__main__":
    asyncio.run(main())
