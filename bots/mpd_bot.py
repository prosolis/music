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

    mpd = mpdproxy.MPDProxy()
    current_fingerprint = await mpd.mpd_get_fingerprint() 
    current_title, current_artist = await mpd.mpd_get_current_song_title_and_artist()

    await check_song_exists(current_fingerprint, current_title, current_artist)
    await update_play_history(current_fingerprint, current_title, current_artist)

    await mpd.mpd_connection_close()

    while True:
        mpd.mpd_connection_open()

        result_fingerprint = await mpd.mpd_get_fingerprint()

        if(current_fingerprint != result_fingerprint):
            logger.info("Playing different song")

            current_fingerprint = result_fingerprint
            current_title, current_artist = await mpd.mpd_get_current_song_title_and_artist()

            await check_song_exists(current_fingerprint, current_title, current_artist)
            await update_play_history(current_fingerprint, current_title, current_artist)

        else:
            logger.info("Same song, skipping checks and updates")

        next_song_title = await mpd.mpd_next_song_info()

        if(next_song_title is None):
            logger.info("Reached the end of the playlist")
            await mpd.mpd_shuffle_playlist()

        await mpd.mpd_connection_close()
        logger.info("Starting thread sleep for 1 minute and 30 seconds")

        await asyncio.sleep(90)

async def check_song_exists(fingerprint, title, artist):
    logger = logging.getLogger('MPDBot')

    load_dotenv()
    postgres = postgresproxy.PostgresProxy(
        user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))

    await postgres.artist_exists(artist)

    await postgres.song_exists(title, artist, fingerprint)

    await postgres.postgres_connection_close()

    logger.info("%s by %s exists inside DB", title, artist)
    logger.info("Finished check_song_exists")

async def update_play_history(fingerprint, title, artist):
    logger = logging.getLogger('MPDBot')

    load_dotenv()
    postgres = postgresproxy.PostgresProxy(
        user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))
    
    await postgres.insert_play_history(title, artist, fingerprint)

    logger.info("Finished update_play_history")


if __name__ == "__main__":
    asyncio.run(main())
