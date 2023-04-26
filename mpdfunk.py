"""mpdfunk provides basic connectivity and song information from a locally running MPD instance"""
from mpd import MPDClient
import logging

log_format = '%(asctime)s %(message)s'
log_level = 10
logging.basicConfig(format=log_format,level=log_level)
logger = logging.getLogger('MPDProBot')
logger.info("MPD Bot has started")

def mpd_connection_close(client):
    """Close network connection to MPD"""
    client.close()
    client.disconnect()

def mpd_song_info(client):
    """Fetch the current song's title, artist, and fingerprint"""
    title = client.currentsong()['title']
    artist = client.currentsong()['artist']
    fingerprint = client.readcomments(client.currentsong()['file'])['acoustid_fingerprint']
    return title,artist,fingerprint

def mpd_album_art(client):
    """Dump the album art to disk"""
    with open("cover.jpg", "wb") as file_open:
        songimagedict = client.readpicture(client.currentsong()['file'])
        songimage = songimagedict["binary"]
        songimage_bytearray = bytearray(songimage)
        file_open.write(songimage_bytearray)
        file_open.close()


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


def main():
    """Bot code"""
    client = MPDClient()
    client.timeout = 999 #set network timeout
    client.idletimeout = None #timeout for fetching the result of the idle command
    client.connect("localhost", 6600) #6600 is the default MPD port


if __name__ == "__main__":
    main()
   