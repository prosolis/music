import glob
import time

from tinytag import TinyTag
import pandas as pd

#Give path to music folder
music_path= "C:\\Users\\Parod\\Music\\*\\*.*"


songs = glob.glob(music_path)
songlist = [] #["Title","Artist","Genre","Duration"]

for track in songs:
    tag = TinyTag.get(track)
    title = tag.title
    artist = tag.artist
    genre = tag.genre
    runtime = time.gmtime(tag.duration)
    duration = time.strftime("%M:%S", runtime)
    entry = [title, artist, genre, duration]
    songlist.append(entry)

df = pd.DataFrame(
    data    = songlist,
    columns = ['title', 'artist', 'genre', 'duration']
 )

fmt_json = df.to_json(
    orient  = "records",
    indent  = 1
)

file = open("./docs/assets/json/songlist.json", "w", encoding="utf-8")
file.write(fmt_json)
file.close()

