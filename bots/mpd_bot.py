"""MPD Bot will run continuously to run background updates and health status of the mpd"""
import asyncio
import logging
import os
from dotenv import load_dotenv

from helpers.musicplayer import mpdproxy
from helpers.postgres import postgresproxy

async def main():
    """Initializes Prosolis Radio Bot for MPD."""
    log_format = '%(asctime)s %(message)s'
    log_level = 10

    logging.basicConfig(format=log_format, level=log_level)
    logger = logging.getLogger('MPDBot')
    logger.info("MPD Bot has started")

#    current_songid 

##    while True:
#      await update_play_history()

#        logger.info("Starting thread sleep for 2 minutes")

#        asyncio.sleep(120)

    await check_song_exists()

async def check_song_exists():
    logger = logging.getLogger('MPDBot')
    mpd = mpdproxy.MPDProxy()

    artist = mpd.mpd_get_artist_info()

    load_dotenv()
    postgres = postgresproxy.PostgresProxy(
        user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))

    result = postgres.artist_exists

    if(postgres.artist_exists == "f"):
    
        logger.info("Add new artist")
    
    mpd.mpd_connection_close()


if __name__ == "__main__":
    asyncio.run(main())
