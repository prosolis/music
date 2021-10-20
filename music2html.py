import glob
from tinytag import TinyTag
import pandas as pd
import time

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

df = pd.DataFrame(songlist, columns =['Title', 'Artist', 'Genre', 'Duration (M:S)'])
df = df.sort_values(by=['Genre','Title'], kind='stable')

html = df.to_html(classes='table table-striped', table_id='trackTable', header=True, index=False)

html = df.style.set_properties(**{'font-size': '12pt', 'font-family': 'Calibri','border-bottom': '1px solid #666','border-collapse': 'collapse', 'width': '30%', 'padding': '10px', 'background-color': '#f3f3f3'}).render()

#html = df.to_html(classes='table table-striped', table_id='trackTable', header=True, index=False)

file = open("index.html", "w", encoding="utf-8")
file.write(html)
file.close()

