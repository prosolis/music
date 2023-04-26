"""Module providing logging for development and debugging"""
import logging
import asyncio

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from helpers import live_broadcast, live_chat

async def main():
    """Intializes Radio Proslis Bot for Youtube."""
    log_format = '%(asctime)s %(message)s'
    log_level = 10

    logging.basicConfig(format=log_format,level=log_level)
    logger = logging.getLogger('YoutubeProBot')
    logger.info("YouTube Bot has started")

    scopes = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"]

    # TODO(camcast): Use dotenv here instead of clear text.
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "/home/cameron/GitHub/music/client_secrets.json"

    # TODO(camcast): Make this into a seperate object class to be used globally.
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        credentials=credentials)

    #Need to catch when authorization code doesnt work
    live_chat_id = await live_broadcast.get_live_chatid(youtube)

    await live_chat.get_live_chat_messages(youtube, live_chat_id)

if __name__ == "__main__":
    asyncio.run(main())
