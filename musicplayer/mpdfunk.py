# pylint: disable=no-member
"""mpdfunk provides basic connectivity and song information from a locally running MPD instance"""
import logging
from mpd import MPDClient, MPDError

class MPDProxy:
    """Class representing proxy connection to MPD"""
    async def __init__(self, host="localhost", port="6600", timeout=999):
        log_format = '%(asctime)s %(message)s'
        log_level = 10
        logging.basicConfig(format=log_format,level=log_level)
        logger = logging.getLogger('MPDProxy')

        self._client = MPDClient()
        self._host = host
        self._port = port

        self._client.timeout = timeout
        self.mpd_connection_open()
        logger.info("MPD Proxy initalized")

    async def mpd_connection_open(self):
        """Sets up connect to MPD"""
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
        logger = logging.getLogger('MPDProBot')
        self._client.close()
        self._client.disconnect()
        logger.warning("MPD localhost has been manually disconnected")

    async def mpd_song_info(self):
        """Fetch the current song's title, artist, and fingerprint"""
        title = self._client.currentsong()['title']
        artist = self._client.currentsong()['artist']
        fingerprint = self._client.readcomments(
            self._client.currentsong()['file'])['acoustid_fingerprint']
        return title,artist,fingerprint

    async def mpd_album_art(self):
        """Dump the album art to disk"""
        logger = logging.getLogger('MPDProBot')
        try:
            with open("cover.jpg", "wb") as file_open:
                songimagedict = self._client.readpicture(self._client.currentsong()['file'])
                songimage = songimagedict["binary"]
                songimage_bytearray = bytearray(songimage)
                file_open.write(songimage_bytearray)
                file_open.close()
        except OSError as oserror:
            logger.error("Could not open %s cover.png: %s", 
                         self._client.currentsong()['title'], oserror)

def mpd_playlist_info(client):
    """Return the MPD playlist"""
    return client.playlist()

def mpd_next_song_info(client):
    """Pull the next song's artist and title"""
    artist = client.playlistid(client.status()['nextsongid'])[0]['artist']
    title = client.playlistid(client.status()['nextsongid'])[0]['title']
    return title, artist

def mpd_fetch_current_song_id(client):
    """Pull the current song ID"""
    return client.currentsong()['id']

def mpd_fetch_song_fingerprint(client):
    """Fetch current song acoustic fingerprint"""
    return client.readcomments(client.currentsong()['file'])['acoustid_fingerprint']

mpdproxy = MPDProxy()
