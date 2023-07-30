# pylint: disable=no-member
"""mpdproxy provides basic connectivity and song information from a locally running MPD instance"""
import logging
from mpd import MPDClient, MPDError

class MPDProxy:
    """Class representing proxy connection to MPD"""
    def __init__(self, host="localhost", port="6600", timeout=999):
        log_format = '%(asctime)s %(message)s'
        log_level = 10
        logging.basicConfig(format=log_format, level=log_level)
        logger = logging.getLogger('MPDProxy')

        self._client = MPDClient()
        self._host = host
        self._port = port

        self._client.timeout = timeout
        self.mpd_connection_open()
        logger.info("MPD Proxy initialized")

    def mpd_connection_open(self):
        """Open network connection to MPD"""
        logger = logging.getLogger('MPDProxy')
        try:
            self._client.connect(self._host, self._port)
        except IOError as ioerror:
            logger.error("Could not connect to %s: %s", self._host, ioerror)
        except MPDError as mpderror:
            logger.error("Could not connect to %s: %s", self._host, mpderror)
        logger.info("MPD Proxy connected")

    async def mpd_connection_close(self):
        """Close network connection to MPD"""
        logger = logging.getLogger('MPDProxy')
        self._client.close()
        self._client.disconnect()
        logger.warning("MPD localhost has been manually disconnected")

    async def mpd_get_current_song_title_and_artist(self):
        """Fetch the current song's title and artist"""
        title = self._client.currentsong()['title']
        artist = self._client.currentsong()['artist']
        return title, artist

    async def mpd_get_fingerprint(self):
        """Fetch the current song's fingerprint"""
        fingerprint = self._client.readcomments(
            self._client.currentsong()['file'])['acoustid_fingerprint']
        return fingerprint

    async def mpd_get_artist_info(self):
        """Fetch the current song's artist"""
        artist = self._client.currentsong()['artist']
        return artist

    async def mpd_dump_song_title(self):
        """Dump the song title to disk"""
        logger = logging.getLogger('MPDProxy')
        try:
            with open("songtitle.txt", "wb") as file_open:
                song_title = self._client.currentsong()['title']
                song_title_bytes = bytes(song_title, 'utf-8')
                file_open.write(song_title_bytes)
                file_open.close()
        except OSError as oserror:
            logger.error("Could not open songtitle.txt: %s", oserror)

    async def mpd_dump_song_artist(self):
        """Dump the song artist to disk"""
        logger = logging.getLogger('MPDProxy')
        try:
            with open("songartist.txt", "wb") as file_open:
                song_artist = self._client.currentsong()['artist']
                song_artist_bytes = bytes(song_artist, 'utf-8')
                file_open.write(song_artist_bytes)
                file_open.close()
        except OSError as oserror:
            logger.error("Could not open songartist.txt: %s", oserror)

    async def mpd_dump_album_art(self):
        """Dump the album art to disk"""
        logger = logging.getLogger('MPDProxy')
        try:
            with open("cover.jpg", "wb") as file_open:
                album_art_dict = self._client.readpicture(self._client.currentsong()['file'])
                album_art = album_art_dict["binary"]
                album_art_bytearray = bytearray(album_art)
                file_open.write(album_art_bytearray)
                file_open.close()
        except OSError as oserror:
            logger.error("Could not open %s cover.png: %s",
                         self._client.currentsong()['title'], oserror)
        except KeyError as keyerror:
            logger.error("Album art is missing for %s by %s @Prosolis: %s",
                        self._client.currentsong()['title'],
                        self._client.currentsong()['artist'],
                        keyerror)

    async def mpd_playlist_info(self):
        """Return the current MPD playlist"""
        return self._client.playlist()

    async def mpd_next_song_title(self):
        """Fetch the next song's artist and title"""
        logger = logging.getLogger('MPDProxy')
        title = None

        try:
            title = self._client.playlistid(self._client.status()['nextsongid'])[0]['title']
        except KeyError as key_error:
            logger.info("Unable to get next song title due to KeyError: %s", key_error)

        return title

    async def mpd_shuffle_playlist(self):
        """Takes the current playlist and shuffles it"""
        self._client.shuffle()
