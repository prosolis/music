# pylint: disable=no-member,broad-exception-caught
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
        logger.info("MPD localhost has been manually disconnected")

    async def mpd_get_current_song_title_and_artist(self):
        """Fetch the """
        logger = logging.getLogger('MPDProxy')
        try:
            title = self._client.currentsong()['title']
            artist = self._client.currentsong()['artist']
        except KeyError as key_error:
            logger.info("Unable to get current song's title and artist due to KeyError: %s",
                        key_error)

        except MPDError as mpderror:
            logger.error("MPD Error when checking the current song title and artist: %s",  mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

        return title, artist

    async def mpd_get_fingerprint(self):
        """Fetch the current song's fingerprint"""
        logger = logging.getLogger('MPDProxy')
        try:
            fingerprint = self._client.readcomments(
                self._client.currentsong()['file'])['acoustid_fingerprint']
        except KeyError as key_error:
            logger.info("Unable to get next song fingerprint due to KeyError: %s", key_error)

        except MPDError as mpderror:
            logger.error("MPD Error when checking the current song fingerprint: %s",  mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

        return fingerprint

    async def mpd_get_artist_info(self):
        """Fetch the current song's artist"""
        logger = logging.getLogger('MPDProxy')
        try:
            artist = self._client.currentsong()['artist']

        except KeyError as key_error:
            logger.info("Unable to get artist due to KeyError: %s", key_error)

        except MPDError as mpderror:
            logger.error("MPD Error when checking the current song artist: %s",  mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

        return artist

    async def mpd_dump_song_title(self, folder_path):
        """Dump the song title to disk"""
        logger = logging.getLogger('MPDProxy')
        try:
            file_name = "songtitle.txt"
            file_path = folder_path + "/" + file_name

            with open(file_path, "wb+") as file_open:
                song_title = self._client.currentsong()['title']
                song_title_bytes = bytes(song_title, 'utf-8')
                file_open.write(song_title_bytes)
                file_open.close()
        except OSError as oserror:
            logger.error("Could not open songtitle.txt: %s", oserror)

        except MPDError as mpderror:
            logger.error("MPD Error when shuffling the playlist: %s", mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

    async def mpd_dump_song_artist(self, folder_path):
        """Dump the song artist to disk"""
        logger = logging.getLogger('MPDProxy')
        try:
            file_name = "songartist.txt"
            file_path = folder_path + "/" + file_name

            with open(file_path, "wb+") as file_open:
                song_artist = self._client.currentsong()['artist']
                song_artist_bytes = bytes(song_artist, 'utf-8')
                file_open.write(song_artist_bytes)
                file_open.close()

        except OSError as oserror:
            logger.error("Could not open songartist.txt: %s", oserror)

        except MPDError as mpderror:
            logger.error("MPD Error when shuffling the playlist: %s", mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

    async def mpd_dump_album_art(self, folder_path):
        """Dump the album art to disk"""
        logger = logging.getLogger('MPDProxy')
        try:
            file_name = "cover.jpg"
            file_path = folder_path + "/" + file_name

            with open(file_path, "wb+") as file_open:
                album_art_dictionary = self._client.readpicture(self._client.currentsong()['file'])

                if not album_art_dictionary:
                    album_art_dictionary = self._client.albumart(self._client.currentsong()['file'])

                album_art = album_art_dictionary["binary"]
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

        except MPDError as mpderror:
            logger.error("MPD Error when shuffling the playlist: %s", mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

    async def mpd_playlist_info(self):
        """Return the current MPD playlist"""
        logger = logging.getLogger('MPDProxy')
        try:
            return self._client.playlist()
        except MPDError as mpderror:
            logger.error("MPD Error when getting playlist info: %s",
                         mpderror)
        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

    async def mpd_next_song_title(self):
        """Fetch the next song's artist and title"""
        logger = logging.getLogger('MPDProxy')
        try:
            title = self._client.playlistid(self._client.status()['nextsongid'])[0]['title']
        except KeyError as key_error:
            logger.info("Unable to get next song title due to KeyError: %s", key_error)

        except MPDError as mpderror:
            logger.error("MPD Error when checking the next song title: %s",  mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

        return title

    async def mpd_shuffle_playlist(self):
        """Shuffle the current playlist"""
        logger = logging.getLogger('MPDProxy')
        try:
            self._client.shuffle()
        except MPDError as mpderror:
            logger.error("MPD Error when shuffling the playlist: %s", mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

    async def mpd_is_last_song(self):
        """Takes the current song and sees if it is the last in the playlist"""
        logger = logging.getLogger('MPDProxy')

        try:
            current_song_position = self._client.status()['song']
            #Add one here as song returns the array slot and not the mpc position.
            current_song_position = int(current_song_position) + 1

            songs = self._client.playlist()
            total_songs = len(songs)

            if (total_songs - current_song_position) == 0:
                return True

        except MPDError as mpderror:
            logger.error("MPD Error when check is this the last song in the playlist: %s",
                            mpderror)

        except Exception as exception:
            logger.error("Unexpected Error: %s", exception)

        return False
