"""python-mpd2 library"""
#import os
from mpd import MPDClient

#def mpdconnectionclose():
#    """Close network connection to MPD"""
#    client.close()
#    client.disconnect()

def mpdsonginfo(client):
    """Fetch the current song's title, artist, and fingerprint"""
    title = client.currentsong()['title']
    artist = client.currentsong()['artist']
    fingerprint = client.readcomments(client.currentsong()['file'])['acoustid_fingerprint']
    return title,artist,fingerprint

def mpdalbumart(client):
    """Dump the album art to disk"""
    file_open = open("cover.jpg", "wb")
    songimagedict = client.readpicture(client.currentsong()['file'])
    songimage = songimagedict["binary"]
    songimage_bytearray = bytearray(songimage)
    file_open.write(songimage_bytearray)
    file_open.close()


def mpdplaylistinfo(client):
    """Return the MPD playlist"""
    return client.playlist()

def mpdnextsonginfo(client):
    """Pull the next song's artist and title"""
    artist = client.playlistid(client.status()['nextsongid'])[0]['artist']
    title = client.playlistid(client.status()['nextsongid'])[0]['title']
    return title, artist

def mpdfetchcurrentsongid(client):
    """Pull the current song ID"""
    return client.currentsong()['id']

def mpdfetchsongfingerprint(client):
    """Fetch current song acoustic fingerprint"""
    return client.readcomments(client.currentsong()['file'])['acoustid_fingerprint']


def main():
    """Bot code"""
    client = MPDClient()
    client.timeout = 999 #set network timeout
    client.idletimeout = None #timeout for fetching the result of the idle command
    client.connect("localhost", 6600) #6600 is the default MPD port
    #print("Hello World!")
    #mpdconnectionopen()
    title, artist, fingerprint = mpdsonginfo(client)
    print(title, artist, fingerprint)
    nexttitle, nextartist = mpdnextsonginfo(client)
    print(nexttitle, nextartist)
   # print(mpdPlayListInfo())
    print(mpdfetchsongfingerprint(client))
    mpdalbumart(client)

if __name__ == "__main__":
    main()
   