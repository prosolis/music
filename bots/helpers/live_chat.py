"""Modules for interacting with the liveChatMessages api"""
# pylint: disable=too-many-arguments
import asyncio
import logging
import os
import requests
from dotenv import load_dotenv
from helpers.musicplayer import mpdproxy
from helpers.postgres import postgresproxy

# TODO(camcast): #3 make one youtube_bot class + migrate youtube helpers into that file
# TODO(camcast): #4 Put sending of message to a helper function  

async def get_live_chat_messages(youtube, live_chatid):
    """Get YouTube Live Chat Messages"""
    logger = logging.getLogger('YoutubeProBot')

    try:
        next_page_token = ''

        while True:
            if not next_page_token:
                request = youtube.liveChatMessages().list(
                    liveChatId=live_chatid,
                    part="snippet,authorDetails",
                    maxResults=1000
                )
                response = request.execute()
                logger.debug("Get LiveChatMessage list - Success!")

            else:
                request = youtube.liveChatMessages().list(
                    liveChatId=live_chatid,
                    part="snippet,authorDetails",
                    maxResults=1000,
                    pageToken=next_page_token
                )
                response = request.execute()
                logger.debug("Get LiveChatMessage NextPage list - Success!")

            if response:
                await discover_command_requests(youtube, response, live_chatid)

            next_page_token = response["nextPageToken"]
            wait_time = response["pollingIntervalMillis"]/1000
            await asyncio.sleep(wait_time)

    except requests.exceptions.HTTPError as request_httperror:
        logger.error(str(request_httperror))
        return

async def discover_command_requests(youtube, response, live_chatid):
    """Discover any commands passed into live chat"""
    logger = logging.getLogger('YoutubeBot')

    test_command_str    = "!test"
    like_command_str    = "!like"
    song_command_str    = "!song"
    artist_command_str  ="!artist"

    for items in response["items"]:
        text_message = items["snippet"]["textMessageDetails"]["messageText"]
        is_chat_owner = items["authorDetails"]["isChatOwner"]
        is_chat_moderator = items["authorDetails"]["isChatModerator"]
        author_id = items["authorDetails"]["channelId"]

        if text_message == test_command_str and (is_chat_owner or is_chat_moderator):
            logger.debug("Found test command")
            await respond_test_command(youtube, live_chatid)

        elif text_message == like_command_str:
            logger.debug("Found like command")
            await respond_like_command(youtube, live_chatid, author_id)

        elif text_message == song_command_str:
            logger.debug("Found song command")
            await respond_song_command(youtube, live_chatid)

        elif text_message == artist_command_str:
            logger.debug("Found aritst command")
            await respond_artist_command(youtube, live_chatid)

async def respond_test_command(youtube, live_chatid):
    """Logic for test command, returns test message back to bots live chat"""
    logger = logging.getLogger('YoutubeBot')

    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chatid,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": "This is a test message from YoutubeBot"
                    }
                }
            }
        )
        response = request.execute()
        print(response)
        logger.debug("Sent test command response to live stream")

    except requests.exceptions.HTTPError as request_httperror:
        logger.error(str(request_httperror))

async def respond_like_command(youtube, live_chatid, author_id):
    """Logic for like command, returns a thankful message to youtube live chat"""
    logger = logging.getLogger('YoutubeBot')

    mpd = mpdproxy.MPDProxy()
    fingerprint = await mpd.mpd_get_fingerprint()

    load_dotenv()
    platform_name = 'Youtube'
    postgres = postgresproxy.PostgresProxy(
        user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))
    await postgres.song_likes_command(author_id, platform_name, fingerprint)

    await mpd.mpd_connection_close()
    await postgres.postgres_connection_close()

    message = "Thanks this data will help us continue bringing the best music to Prosolis Radio"

    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chatid,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message
                    }
                }
            }
        )
        response = request.execute()
        print(response)
        logger.debug("Sent like command response to live stream")

    except requests.exceptions.HTTPError as request_httperror:
        logger.error(str(request_httperror))

async def respond_song_command(youtube, live_chatid):
    """Logic for song command, returns song title and artist to the youtube live chat"""
    logger = logging.getLogger('YoutubeBot')

    mpd = mpdproxy.MPDProxy()
    title, artist = await mpd.mpd_song_info()
    await mpd.mpd_connection_close()

    message = f"The current song is {title} by {artist}"

    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chatid,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message
                    }
                }
            }
        )
        response = request.execute()
        print(response)
        logger.debug("Sent song command response to live stream")

    except requests.exceptions.HTTPError as request_httperror:
        logger.error(str(request_httperror))

async def respond_artist_command(youtube, live_chatid):
    """Logic for artist command, returns artist socials to youtube live chat"""
    logger = logging.getLogger('YoutubeBot')

    mpd = mpdproxy.MPDProxy()
    artist = await mpd.mpd_get_artist_info()

    load_dotenv()
    postgres = postgresproxy.PostgresProxy(
        user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))
    socials = await postgres.artist_info_command(artist)

    await mpd.mpd_connection_close()
    await postgres.postgres_connection_close()

    message = f'''Artist Name: {artist} \n
    YouTube: {socials[0]}'''

    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chatid,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message
                    }
                }
            }
        )
        response = request.execute()
        print(response)
        logger.debug("Sent artist command response to live stream")

    except requests.exceptions.HTTPError as request_httperror:
        logger.error(str(request_httperror))
