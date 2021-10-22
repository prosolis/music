# All your imports
import sys
import musicpd
from decouple import config
from numpy.core.records import recarray
from twitchio.ext import commands
import requests
import os
from tinytag import TinyTag
import random
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import select
import socket
import pandas as pd
from datetime import datetime
import time
import csv


# Sets up the bot from env
bot = commands.Bot(
    irc_token= config('TMI_TOKEN'),
    client_id= config('BEARER_ID'),
    nick= config('BOT_NICK'),
    prefix=config('BOT_PREFIX'),
    initial_channels=[config('CHANNEL')]
)

mpd = musicpd.MPDClient()
mpd.socket_timeout = 10
mpd.connect()
mpd.update()
print(f'MPD Version == {mpd.mpd_version}')

mpd.repeat(1)
#mpd.random(1)
mpd.crossfade(10)
#mpd.setvol(100)
mpd.disconnect()

df = pd.read_csv('requests.csv')
req_dict = dict(df.values) #{Song name: total # Times requested}

music_path= "C:/Users/Parod/Music"
songlist = [] #["Title","Artist","Duration","Path"]

playlist = [] #mpd playlist

song_reqs = {} #{songid: user who requested}

latest_reqs = {} #{user who requested: songid}

req_timer = {} #{song name: clock time requested}

genre = "" #set from genre of the day

fuzzyconfidence = 95 #sets fuzzywuzzy param, 85 works good

subscribers = {} #Subscriber Name : # of requests they have
subscribers[config('CHANNEL')] = 1000

played = [] #ids of song played

twitch = { #Twitch artist promo
    "ArCaJazz" : "Please check out more ArCaJazz goodness via the following links: • Twitch: https://twitch.tv/arcajazz • Spotify: Ariel Calabria • Bandcamp: https://arcajazz.bandcamp.com/ • Instagram: arcajazz",
    "CallsignScarecrow" : "Please check out more CallsignScarecrow goodness via the following links: • Twitch: https://www.twitch.tv/callsignscarecrow • Spotify: https://open.spotify.com/artist/2ATXEER8LOT0lZxgxwNuSU • Aubryn's Twitch (Musician featured in 'You Haunt Me'): https://www.twitch.tv/aubrynmusic",
    "Calvin Thomas" : "Please check out more Calvin Thomas goodness via the following links: • Twitch: https://www.twitch.tv/calvinthomasmusic • Spotify: https://spoti.fi/3unhJF1 • Bandcamp: https://calvinthomasmusic.bandcamp.com/ • Twitter: https://twitter.com/calvinthomasmus • Instagram: https://www.instagram.com/calvinthomasmusic/ • Website: https://calvinthomasmusic.com/home",
    "Chika_Tatsuya" : "Please check out more Chika_Tatsuya goodness via the following links: • Twitch: https://twitch.tv/chika_tatsuya • Bandcamp: https://chikatanaka.bandcamp.com/",
    "FiKTaH" : "Please check out more FiKTaH goodness via the following links: • Twitch: https://twitch.tv/fiktah",
    "gabcreates" : "Please check out more gabcreates goodness via the following links: • Twitch: https://twitch.tv/gabcreates • Spotify: https://open.spotify.com/artist/4tLANANLwM1pBnb7csmCSc?si=GaCLhILvRJGiHgyD6aeiLg&dl_branch=1 • Bandcamp: https://gabcreates.bandcamp.com/ • Beacons: https://beacons.ai/gabcreates",
    "JBAUJBAUJBAU" : "Please check out more JBAUJBAUJBAU goodness via the following links: • Twitch: https://twitch.tv/jbaujbaujbau • Beacons: https://beacons.ai/jeremyseventy • Bandcamp: https://jeremyseventy.bandcamp.com/",
    "JuanorPiano" : "Please check out more JuanorPiano goodness via the following links: • Twitch: https://twitch.tv/juanorpiano • Bandcamp: https://juanortiz.bandcamp.com/",
    "kellygates47" : "Please check out more kellygates47 goodness via the following links: • Twitch: https://twitch.tv/kellygates47 • Spotify:  https://open.spotify.com/artist/5Vh7pAIeanZ3OJWkFXDEQ4?si=8v7cEYjBT-OApEWj7UAJLA • Bandcamp: https://kellygates.bandcamp.com/ • Website: https://kellygatesmusic.com",
    "Keyboard Grinder" : "Please check out more Keyboard Grinder goodness via the following links: • Twitch: https://twitch.tv/keyboardgrinder",
    "MalaykaMusic" : "Please check out more MalaykaMusic goodness via the following links: • Twitch: https://twitch.tv/malaykamusic • Spotify: https://open.spotify.com/artist/4DJk09zggqa3otcA3gtPNM?si=NjJwJur-QoG50zDULWGIcg&dl_branch=1 • Instagram: www.instagram/com/malaykamusic • Apple Music: https://music.apple.com/us/artist/malayka/1525654543 • Youtube: www.youtube.com/c/malaykamusic",
    "MikeBassMusic" : "Please check out more MikeBassMusic goodness via the following links: • Twitch: https://twitch.tv/mikebassmusic",
    "MyManEvans" : "Please check out more StringPlayerGamer goodness via the following links: • Twitch: https://twitch.tv/mymanevans • Youtube: https://www.youtube.com/channel/UCN_H0p4O4jRn2VOd3KDp28A",
    "OrchKeystraMusic" : "Please check out more OrchKeystraMusic goodness via the following links: • Twitch: https://twitch.tv/OrchKeystraMusic • Patreon: https://patreon.com/OrchKeystraMusic • Youtube: https://youtube.com/OrchKeystraMusic • Instagram: https://www.instagram.com/orchkeystra_music",
    "RachelGraceViolin" : "Please check out more RachelGraceViolin goodness via the following links: • Twitch: https://twitch.tv/rachelgraceviolin • Spotify: https://open.spotify.com/artist/0H4gsuLu12OvThdJfxsP2C • Bandcamp: https://rachelgraceviolin.bandcamp.com/ • Youtube: https://www.youtube.com/c/RachelGrace",
    "RamonWasHier" : "Please check out more RamonWasHier goodness via the following links: • Twitch: https://twitch.tv/RamonWasHier • Spotify: Spotify: https://open.spotify.com/artist/1ohEmpReONCvx9qjzlLi1r • Website: https://ramonwashier.com/",
    "Regular_Human_Music" : "Please check out more Regular_Human_Music goodness via the following links: • Twitch: https://twitch.tv/regular_human_music",
    "StringPlayerGamer" : "Please check out more StringPlayerGamer goodness via the following links: • Twitch: https://twitch.tv/StringPlayerGamer • Spotify: https://open.spotify.com/artist/4tyZ8F1QPVTJ1EbkrlnpMd • YouTube: https://www.youtube.com/thestringplayergamer • Bandcamp(s): https://diwadeleon.bandcamp.com/ https://stringplayergamer.bandcamp.com/",
    "The Complements" : "Please check out more The Complements goodness via the following links: • Twitch: https://twitch.tv/thecomplements • Spotify: https://open.spotify.com/artist/0tU85IJB7ZSiF8vzN8JbdV?si=G8ffSaD8RHeL3R7DEBUOWA • Apple Music: https://music.apple.com/us/artist/the-complements/1244374343 • Youtube: http://youtube.com/thecomplements • Instagram: http://instagram.com/wearethecomplements",
    "TheFunkySpud" : "Please check out more TheFunkySpud goodness via the following links: • Twitch: https://twitch.tv/thefunkyspud • Youtube: https://www.youtube.com/c/thefunkyspud",
    "Windy_Harper" : "Please check out more Windy Harper goodness via the following links: • Twitch: https://www.twitch.tv/windy_harper • Instagram: https://www.instagram.com/windyharper15/ • Youtube: www.youtube.com/windyharper",
    "YentingLo" : "Please check out more YentingLo goodness via the following links: • Twitch: https://twitch.tv/yentinglo • Spotify: https://open.spotify.com/artist/6W7lSbguF67nqkK6djqd8z?si=L7DNRY9yQx24NE8FmWQFDA&dl_branch=1 • Bandcamp: https://yentinglo.bandcamp.com/ • Website: https://yentinglo.net/ • Youtube: https://www.youtube.com/YenTingLo • Instagram: https://www.instagram.com/yenting.lo/"
}

reqpos = 0 #last pos where sr went to

gflag = False

@bot.event
async def event_ready():
    # Runs when bot connects to channel
    print(f"{config('BOT_NICK')} is online! at http://twitch.tv/{config('CHANNEL')}")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(config('CHANNEL'), f"/me I'm back!") # Sends intro message

@bot.event
async def event_message(ctx):
    # Runs every time a message is sent in chat.
    global mpd, songlist, music_path, fuzzyconfidence, twitch, reqpos, played, gflag
    
    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == config('BOT_NICK').lower():
        return

    # Prints chat in terminal
    print(f"{ctx.author.name}: {ctx.content}")
    #print(ctx.raw_data)

    if gflag== True:
        mpd.connect()
        
        currentsong = mpd.currentsong()['title']
        currentartist = mpd.currentsong()['artist']
        pos = int(mpd.status()['nextsongid'])
        nextsong = mpd.playlistid(pos)[0]['title']
        nextartist = mpd.playlistid(pos)[0]['artist']
        currentid = mpd.currentsong()['id']

        if currentid not in played:            
            if song_reqs.__contains__(currentid):
                await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong} requested by {song_reqs[currentid]}')
            else:
                await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong}')

            if twitch.__contains__(currentartist):
                await ctx.channel.send(f'{twitch[currentartist]}')

            file1 = open("song_artist.txt","w")
            file1.write(currentartist)
            file1.close()

            file2 = open("song_title.txt","w")
            file2.write(currentsong)
            file2.close()

            file3 = open("song_artist_next.txt","w")
            file3.write(nextartist)
            file3.close()

            file4 = open("song_title_next.txt","w")
            file4.write(nextsong)
            file4.close()
            played.append(currentid)

        mpd.disconnect()
            
    #CHANNEL POINTS SONG REQUEST
    if "custom-reward-id=9853b03b-4795-4fbf-85e0-631ebd5a93c7" in ctx.raw_data:
        mpd.connect()
        data = ctx.raw_data
        sname = data.split(":")[-1]
        
        s_song = ""

        flag = False

        current_time = time.time()

        for songs in songlist:
            if fuzz.token_set_ratio(sname,songs[0])>fuzzyconfidence:
                if req_timer.__contains__(songs[0]) and current_time-req_timer[songs[0]]<14400:
                    await ctx.send(f'"{songs[0]}" has already been requested recently by another person. please request another song!')
                    return
                else:
                    s_song = songs[0]
                    print(s_song)
                    location = songs[3]
                    

                    cpos = int(mpd.currentsong()['pos'])
                    song_info = mpd.playlistsearch('file', location)
                    song_id = song_info[0]['id']
                    
                    if cpos > reqpos:
                        mpd.moveid(song_id, cpos+1)
                        reqpos = cpos+1
                        flag = True
                    else:
                        mpd.moveid(song_id,reqpos+1)
                        reqpos += 1
                        flag = True

                    playlist = mpd.playlistid()

                    req_dict[songs[0]] += 1

                    req_timer[songs[0]] = current_time

                    for music in playlist:
                        if int(music['pos']) == reqpos:
                            song_reqs[music['id']]= ctx.author.name
                            latest_reqs[ctx.author.name] = music['id']

        if flag==True:
            await ctx.channel.send(f'"{s_song}" added to the playlist!')
        else:
            await ctx.channel.send(f'No match found for "{sname}"') 
        mpd.disconnect()

    # Handles bot commands
    await bot.handle_commands(ctx)

@bot.event
async def event_raw_pubsub(self, message):
    global mpd, songlist, music_path, reqpos, song_reqs, playlist, req_dict, req_timer

    sname = ""
    bits_used = ""
    flag = False
    current_time = time.time()
    s_song = ""
    author = ""

    mpd.connect()

    if message['type'] == 'MESSAGE':
        data = json.loads(message['data']['message'])

        if 'bits_used' in data['data']:
            bits_used = data['data']['bits_used']
            author = data['data']['user_name']
            context = data['data']['chat_message']
            sname = context.split('"')[1]

    if int(bits_used)>=100:
        
        for songs in songlist:
            if fuzz.token_set_ratio(sname,songs[0])>fuzzyconfidence:
                if req_timer.__contains__(songs[0]) and current_time-req_timer[songs[0]]<14400:
                    await message.channel.send(f'"{songs[0]}" has already been requested recently by another person. please request another song!')
                    return
                else:
                    s_song = songs[0]
                    location = songs[3]

                    cpos = int(mpd.currentsong()['pos'])
                    song_info = mpd.playlistsearch('file', location)
                    song_id = song_info[0]['id']
                    
                    if cpos > reqpos:
                        mpd.moveid(song_id, cpos+1)
                        reqpos = cpos+1
                        flag = True
                    else:
                        mpd.moveid(song_id,reqpos+1)
                        reqpos += 1
                        flag = True

                    playlist = mpd.playlistid()

                    req_dict[songs[0]] += 1

                    req_timer[songs[0]] = current_time

                    for music in playlist:
                        if int(music['pos']) == reqpos:
                            song_reqs[music['id']]= author
                            latest_reqs[author] = music['id']

    mpd.disconnect()
    if flag == True:    
        await message.channel.send(f'Thank you for the bits {author}! {s_song} added to the playlist!')
    else:
        await message.channel.send(f'Thank you for the bits {author}!')

# BOT COMMANDS
# Test command [ANY]
@bot.command(name='test')
async def test(ctx):
    await ctx.send('test passed!')

# Song request [ANY]
@bot.command(name='sr')
async def sr(ctx, *song):
    global songlist, music_path, reqpos, playlist, song_reqs, req_timer, req_dict, subscribers

    mpd.connect()

    currentsong = mpd.currentsong()['title']
    pos = int(mpd.status()['nextsongid'])
    nextsong = mpd.playlistid(pos)[0]['title']

    current_time = time.time()

    sub = int(ctx.author.is_subscriber)

    if subscribers.__contains__(ctx.author.name):
        pass
    else:
        if sub == 1:
            subscribers[ctx.author.name] = 3
        else:
            mpd.disconnect()
            await ctx.send('Please subscribe to use this feature, subcribers get 3 free song requests daily!')
            return

    if subscribers[ctx.author.name]>0:
        if fuzz.token_set_ratio(song,currentsong)>fuzzyconfidence:
            mpd.disconnect()
            await ctx.send(f'Please request a different song as "{song}" is currently playing!')
            return
        elif fuzz.token_set_ratio(song,nextsong)>fuzzyconfidence:
            mpd.disconnect()
            await ctx.send(f'Please request a different song as "{song}" is going to be played next!')
            return
        else:
            for songs in songlist:
                if fuzz.token_set_ratio(song,songs[0])>fuzzyconfidence:
                    if req_timer.__contains__(songs[0]) and current_time-req_timer[songs[0]]<14400:
                        mpd.disconnect()
                        await ctx.send(f'"{songs[0]}" has already been requested recently by another person. please request another song!')
                        return
                    else:
                        location = songs[3]
                        song_info = mpd.playlistsearch('file', location)
                        song_id = song_info[0]['id']

                        cpos = int(mpd.currentsong()['pos'])

                        if cpos > reqpos:
                            mpd.moveid(song_id, cpos+1)
                            reqpos = cpos+1
                        else:
                            mpd.moveid(song_id,reqpos+1)
                            reqpos += 1

                        playlist = mpd.playlistid()

                        subscribers[ctx.author.name] -= 1

                        req_dict[songs[0]] += 1

                        req_timer[songs[0]] = current_time
                        
                        for music in playlist:
                            if int(music['pos']) == reqpos:
                                song_reqs[music['id']]= ctx.author.name
                                latest_reqs[ctx.author.name] = music['id']

                        await ctx.send(f'"{songs[0]}" by {songs[1]} added to the playlist!')
                        mpd.disconnect()
                        return
            mpd.disconnect()
            await ctx.send(f'No match found for "{song}"')
    else:
        mpd.disconnect()
        await ctx.send(f'Your total number of requests has finished for !sr and !rr. Please use channel points or bits to send song requests!')


# Has Song [ANY]
@bot.command(name='hassong')
async def hassong(ctx, song):
    global songlist

    for songs in songlist:
        if fuzz.token_set_ratio(song,songs[0])>fuzzyconfidence:
            await ctx.send(f'Match found! {songs[0]} by {songs[1]}')
            return
    else:
        await ctx.send(f'No match found for {song}')

# Requests [ANY]
@bot.command(name='req')
async def req(ctx):
    global subscribers
    author = ctx.author.name
    sub = int(ctx.author.is_subscriber)

    print(sub)

    if sub == 1:
        if subscribers.__contains__(author):
            await ctx.send(f"You have {subscribers[author]} requests remaining for today!")
        else:
            subscribers[author] = 3
            await ctx.send(f"You have {subscribers[author]} requests remaining for today!")
    else:
        await ctx.send(f"Subscribers get 3 free song requests everyday! Subscribe to get yours!")

# Wrong Song [ANY]
@bot.command(name='wrongsong')
async def wrongsong(ctx):
    global latest_reqs, song_reqs, mpd
    mpd.connect()
    
    if latest_reqs.__contains__(ctx.author.name):
        songid = int(latest_reqs[ctx.author.name])
        title = mpd.playlistid(songid)[0]['title']
        mpd.deleteid(songid)
        req_dict[title] -= 1
        latest_reqs.pop(ctx.author.name)
        song_reqs.pop(str(songid))
        mpd.disconnect()
        await ctx.send('Your last entered song removed from requests')
    else:
        mpd.disconnect()
        await ctx.send("You haven't requested any songs")

# Current Song [ANY]
@bot.command(name='song', aliases=['currentsong'])
async def song(ctx):
    global mpd
    mpd.connect()

    csong = mpd.currentsong()['title']
    cartist = mpd.currentsong()['artist']
    cduration = int(mpd.currentsong()['time'])
    cid = mpd.currentsong()['id']

    mpd.disconnect()

    if song_reqs.__contains__(cid):
        if len(str(cduration%60))==2:
            await ctx.send(f'Current Song: {cartist} - {csong} requested by {song_reqs[cid]} | Duration: {cduration//60}:{cduration%60}m')
        else:
            await ctx.send(f'Current Song: {cartist} - {csong} requested by {song_reqs[cid]} | Duration: {cduration//60}:0{cduration%60}m')
    else:
        if len(str(cduration%60))==2:
            await ctx.send(f'Current Song: {cartist} - {csong} | Duration: {cduration//60}:{cduration%60}m')
        else:
            await ctx.send(f'Current Song: {cartist} - {csong} | Duration: {cduration//60}:0{cduration%60}m')

# Skip Command [ADMIN/MOD]
@bot.command(name='skip')
async def skip(ctx):
    global mpd, playlist, played
    
    if ctx.author.name.lower() == config('CHANNEL') or ctx.author.is_mod == True:
        mpd.connect()
        mpd.next()

        await ctx.send('Song skipped!')

        currentsong = mpd.currentsong()['title']
        currentartist = mpd.currentsong()['artist']
        pos = int(mpd.status()['nextsongid'])
        nextsong = mpd.playlistid(pos)[0]['title']
        nextartist = mpd.playlistid(pos)[0]['artist']
        currentid = mpd.currentsong()['id']

        if currentid not in played:
            if song_reqs.__contains__(currentid):
                await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong} requested by {song_reqs[currentid]}')
            else:
                await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong}')

            if twitch.__contains__(currentartist):
                await ctx.channel.send(f'{twitch[currentartist]}')

            file1 = open("song_artist.txt","w")
            file1.write(currentartist)
            file1.close()

            file2 = open("song_title.txt","w")
            file2.write(currentsong)
            file2.close()

            file3 = open("song_artist_next.txt","w")
            file3.write(nextartist)
            file3.close()

            file4 = open("song_title_next.txt","w")
            file4.write(nextsong)
            file4.close()

            playlist = mpd.playlistid()
            played.append(currentid)

        mpd.disconnect()
        

# Raid Command [ADMIN/MOD]
@bot.command(name='raidsong')
async def raid(ctx):
    global mpd, reqpos, played

    if ctx.author.name.lower() == config('CHANNEL') or ctx.author.is_mod == True:
        mpd.connect()
        pos = int(mpd.currentsong()['pos'])
        mpd.addid("Raid/Beat - Vulpine Skyflight.ogg", pos+1)
        mpd.next()
        currentid = mpd.currentsong()['id']
        played.append(currentid)
        reqpos += 1
        mpd.disconnect()
        await ctx.send('RAID HYPE!')

# Random Request ARTIST [ANY]
@bot.command(name='rr')
async def rr(ctx, artist=None):
    global songlist, mpd, req_dict, req_timer, reqpos, playlist, song_reqs, subscribers
    current_time = time.time()
    mpd.connect()

    currentsong = mpd.currentsong()['title']
    pos = int(mpd.status()['nextsongid'])
    nextsong = mpd.playlistid(pos)[0]['title']

    sub = int(ctx.author.is_subscriber)

    if subscribers.__contains__(ctx.author.name):
        pass
    else:
        if sub == 1:
            subscribers[ctx.author.name] = 3
        else:
            mpd.disconnect()
            await ctx.send('Please subscribe to use this feature, subcribers get 3 free song requests daily!')
            return

    if subscribers[ctx.author.name]>0:
        if artist != None:
            artistsongs = []

            for artists in songlist:
                if fuzz.token_set_ratio(artist,artists[1])>fuzzyconfidence:
                    artistsongs.append(artists)

            #print(artistsongs)
            if not artistsongs:
                mpd.disconnect()
                await ctx.send(f"No songs found in today's playlist from {artist}.")
            else:
                selected = random.choice(artistsongs)

                if (req_timer.__contains__(selected[0]) and current_time-req_timer[selected[0]]<14400) or currentsong == selected[0] or nextsong == selected[0]:
                    artistsongs.remove(selected)
                    if not artistsongs:
                        mpd.disconnect()
                        await ctx.send(f"The artist: {artist} has no other songs which currently do not have cooldown, please select another artist.")
                        return
                    else:
                        selected = random.choice(artistsongs)

                location = selected[3]
                cpos = int(mpd.currentsong()['pos'])
                song_info = mpd.playlistsearch('file', location)
                song_id = song_info[0]['id']
                
                if cpos > reqpos:
                    mpd.moveid(song_id, cpos+1)
                    reqpos = cpos+1
                else:
                    mpd.moveid(song_id,reqpos+1)
                    reqpos += 1

                playlist = mpd.playlistid()
                
                subscribers[ctx.author.name] -= 1

                req_dict[selected[0]] += 1

                req_timer[selected[0]] = current_time
                        
                for music in playlist:
                    if int(music['pos']) == reqpos:
                        song_reqs[music['id']]= ctx.author.name
                        latest_reqs[ctx.author.name] = music['id']

                mpd.disconnect()
                await ctx.send(f'Added "{selected[0]}" by {selected[1]} to queue')
        else:
            artistsongs = []

            for artists in songlist:
                artistsongs.append(artists)

            selected = random.choice(artistsongs)

            if (req_timer.__contains__(selected[0]) and current_time-req_timer[selected[0]]<14400) or currentsong == selected[0] or nextsong == selected[0]:
                artistsongs.remove(selected)
                if not artistsongs:
                    await ctx.send(f"There are no other songs which currently do not have cooldown")
                    return
                else:
                    selected = random.choice(artistsongs)

            location = selected[3]
            cpos = int(mpd.currentsong()['pos'])
            song_info = mpd.playlistsearch('file', location)
            song_id = song_info[0]['id']
            
            if cpos > reqpos:
                mpd.moveid(song_id, cpos+1)
                reqpos = cpos+1
            else:
                mpd.moveid(song_id,reqpos+1)
                reqpos += 1

            playlist = mpd.playlistid()

            subscribers[ctx.author.name] -= 1

            req_dict[selected[0]] += 1

            req_timer[selected[0]] = current_time
                        
            for music in playlist:
                if int(music['pos']) == reqpos:
                    song_reqs[music['id']]= ctx.author.name
                    latest_reqs[ctx.author.name] = music['id']

            mpd.disconnect()
            await ctx.send(f'Added {selected[0]} by {selected[1]} to queue')
    else:
        mpd.disconnect()
        await ctx.send(f'Total number of requests has finished for !sr and !rr. Please use channel points or bits to send song requests!')

# Next Song [ANY]
@bot.command(name='next', aliases=['nextsong'])
async def next(ctx):
    global mpd
    mpd.connect()

    nextsongid = mpd.status()['nextsongid']
    nsong = mpd.playlistid(nextsongid)[0]['title']
    nartist = mpd.playlistid(nextsongid)[0]['artist']
    nduration = int(mpd.playlistid(nextsongid)[0]['time'])

    mpd.disconnect()

    if song_reqs.__contains__(nextsongid):
        if len(str(nduration%60))==2:
            await ctx.send(f'Next Song: {nartist} - {nsong} requested by {song_reqs[nextsongid]} | Duration: {nduration//60}:{nduration%60}m')
        else:
            await ctx.send(f'Next Song: {nartist} - {nsong} requested by {song_reqs[nextsongid]} | Duration: {nduration//60}:0{nduration%60}m')
    else:
        if len(str(nduration%60))==2:
            await ctx.send(f'Next Song: {nartist} - {nsong} | Duration: {nduration//60}:{nduration%60}m')
        else:
            await ctx.send(f'Next Song: {nartist} - {nsong} | Duration: {nduration//60}:0{nduration%60}m')

# Genre [ANY]
@bot.command(name='genre', aliases=['genreoftheday'])
async def genre(ctx):
    await ctx.send(f"Today's genre is {genre}!")

# Set Genre [ADMIN/MOD]
@bot.command(name='setgenre')
async def rr(ctx, genreinput):
    global music_path, songlist, mpd, genre, req_dict, playlist, played, gflag

    mpd.connect()
    
    songlist = []
    randsonglist = []

    if ctx.author.name.lower() == config('CHANNEL') or ctx.author.is_mod == True:
        if genreinput in ["Jazz", "Chill", "Dance", "Metal", "DrumNBass", "Mixes", "ProsoMix", "Twitch", "Weird"]:
            mpd.clear()
            
            genre = genreinput

            files = [os.path.join(f"{music_path}/{genre}/", file) for file in os.listdir(f"{music_path}/{genre}/")]

            random.shuffle(files) #randomized queue

            for file in files:
                file = file.replace(f"{music_path}/","")
                mpd.add(file)

            playlist = mpd.playlistid()

            for songs in playlist:
                print(songs)
                songlist.append([songs['title'],songs['artist'], songs['time'], songs['file']])

            for music in songlist:
                if req_dict.__contains__(music[0]):
                    pass
                else:
                    req_dict[music[0]] = 0

            mpd.play()

            await ctx.send(f"Today's genre has been set to {genre}")

            currentsong = mpd.currentsong()['title']
            currentartist = mpd.currentsong()['artist']
            pos = int(mpd.status()['nextsongid'])
            nextsong = mpd.playlistid(pos)[0]['title']
            nextartist = mpd.playlistid(pos)[0]['artist']
            currentid = mpd.currentsong()['id']

            if currentid not in played:
                if song_reqs.__contains__(currentid):
                    await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong} requested by {song_reqs[currentid]}')
                else:
                    await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong}')

                if twitch.__contains__(currentartist):
                    await ctx.channel.send(f'{twitch[currentartist]}')

                file1 = open("song_artist.txt","w")
                file1.write(currentartist)
                file1.close()

                file2 = open("song_title.txt","w")
                file2.write(currentsong)
                file2.close()

                file3 = open("song_artist_next.txt","w")
                file3.write(nextartist)
                file3.close()

                file4 = open("song_title_next.txt","w")
                file4.write(nextsong)
                file4.close()

                playlist = mpd.playlistid()
                played.append(currentid)

            mpd.disconnect()
            gflag = True

        elif genreinput == "ALL":
            genre = genreinput
            mpd.clear()

            list1 = [os.path.join(f"{music_path}/Jazz/", file) for file in os.listdir(f"{music_path}/Jazz/")]
            list2 = [os.path.join(f"{music_path}/Chill/", file) for file in os.listdir(f"{music_path}/Chill/")]
            list3 = [os.path.join(f"{music_path}/Dance/", file) for file in os.listdir(f"{music_path}/Dance/")]
            list4 = [os.path.join(f"{music_path}/Metal/", file) for file in os.listdir(f"{music_path}/Metal/")]
            list5 = [os.path.join(f"{music_path}/DrumNBass/", file) for file in os.listdir(f"{music_path}/DrumNBass/")]
            files = list1 + list2 + list3 + list4 + list5

            random.shuffle(files) #randomized queue

            for file in files:
                file = file.replace(f"{music_path}/","")
                mpd.add(file)
            
            playlist = mpd.playlistid()
            #print(playlist)

            for songs in playlist:
                print(songs)
                songlist.append([songs['title'],songs['artist'], songs['time'], songs['file']])

            for music in songlist:
                if req_dict.__contains__(music[0]):
                    pass
                else:
                    req_dict[music[0]] = 0

            mpd.play()

            await ctx.send(f"Today's genre has been set to ALL")

            currentsong = mpd.currentsong()['title']
            currentartist = mpd.currentsong()['artist']
            pos = int(mpd.status()['nextsongid'])
            nextsong = mpd.playlistid(pos)[0]['title']
            nextartist = mpd.playlistid(pos)[0]['artist']
            currentid = mpd.currentsong()['id']

            if currentid not in played:
                if song_reqs.__contains__(currentid):
                    await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong} requested by {song_reqs[currentid]}')
                else:
                    await ctx.channel.send(f'Now Playing: {currentartist} - {currentsong}')

                if twitch.__contains__(currentartist):
                    await ctx.channel.send(f'{twitch[currentartist]}')

                file1 = open("song_artist.txt","w")
                file1.write(currentartist)
                file1.close()

                file2 = open("song_title.txt","w")
                file2.write(currentsong)
                file2.close()

                file3 = open("song_artist_next.txt","w")
                file3.write(nextartist)
                file3.close()

                file4 = open("song_title_next.txt","w")
                file4.write(nextsong)
                file4.close()
                played.append(currentid)

            mpd.disconnect()
            gflag = True

        else:
            await ctx.send("Please try again. Available genre inputs are: Jazz, Chill, Dance, Metal, DrumNBass, Weird, ALL")
            mpd.disconnect()
    else:
        await ctx.send("You don't have permission to do that.")
        mpd.disconnect()

# When Song [ANY]
@bot.command(name='when')
async def when(ctx,song):
    global mpd,songlist, playlist
    mpd.connect()

    playlist = mpd.playlistid()

    time = 0

    current = mpd.currentsong()['id']
    startindex = 0
    endindex = 0
    sname = ""

    mpd.disconnect()

    for music in playlist:
        if music['id']==current:
            startindex = playlist.index(music)
            print(startindex)
            break
            
    for x in range(startindex, len(playlist)):
        print(playlist[x]['title'])
        if fuzz.token_set_ratio(song, playlist[x]['title'])>fuzzyconfidence:
            endindex = playlist.index(playlist[x])
            print(endindex)
            sname = playlist[x]['title']
            break

    for x in range(startindex, endindex):
        time += (int(playlist[x]['time'])-10)

    time = int(time)
    #print(time)
    if endindex-startindex<0:
        await ctx.send(f'{song} has already been played and is not in queue, !sr to request')
    else:
        if len(str(time%60))==2:
            await ctx.send(f'{sname} is at {endindex-startindex+1} in the queue and is playing in approximately {time//60} minutes and {time%60} seconds')
        else:
            await ctx.send(f'{sname} is at {endindex-startindex+1} in the queue and is playing in approximately {time//60} minutes and 0{time%60} seconds')
    

# Song Queue [ANY]
@bot.command(name='queue', aliases=['songqueue'])
async def queue(ctx):
    global mpd, music_path, playlist

    mpd.connect()

    playlist = mpd.playlistid()
    current = mpd.currentsong()['id']
    index = 0

    for song in playlist:
        if song['id']==current:
            index = playlist.index(song)
            print(index)
            break
    
    if index+5>=len(playlist):
        d_playlist = playlist + playlist
        queue = d_playlist[index:index+5]
    else:
        queue = playlist[index:index+5]
    
    #print(queue)

    mpd.disconnect()

    await ctx.send(f"Song Queue: #1 {queue[0]['title']}, #2 {queue[1]['title']}, #3 {queue[2]['title']}, #4 {queue[3]['title']}, #5 {queue[4]['title']}")

# Most Requested Songs [ANY]
@bot.command(name='top5')
async def top5(ctx):
    global req_dict

    slist = list(req_dict.items())
    slist.sort(key = lambda x: x[1])

    await ctx.send(f"Most Requested: #1 {slist[-1][0]}, #2 {slist[-2][0]}, #3 {slist[-3][0]}, #4 {slist[-4][0]}, #5 {slist[-5][0]}")

# Least Requested Songs [ANY]
@bot.command(name='bottom5')
async def bottom5(ctx):
    global req_dict

    slist = list(req_dict.items())
    slist.sort(key = lambda x: x[1])

    await ctx.send(f"Least Requested: #1 {slist[0][0]}, #2 {slist[1][0]}, #3 {slist[2][0]}, #4 {slist[3][0]}, #5 {slist[4][0]}")

# Special Kill command to turn off bot. Only allows the streamer to turn it off. Others get a fun reply.
@bot.command(name='kill')
async def kill(ctx):
    global mpd, req_dict, df

    mpd.connect()

    if ctx.author.name.lower() == config('CHANNEL'):
        print('You are exiting the program.')
        await ctx.send("/me i'll be back with more music!")

        keys = list(req_dict.keys())
        values = list(req_dict.values())

        data = []

        for x in range(len(keys)):
            data.append([keys[x],values[x]])

        df = pd.DataFrame(data, columns =['Song_Name','Times_Played'])

        #print(df)
        df.to_csv('requests.csv',index=False)

        mpd.clear()
        mpd.disconnect()
        sys.exit(0)
    else:
        mpd.disconnect()
        await ctx.send("You don't have permission to do that.")

if __name__ == "__main__":
    bot.run()