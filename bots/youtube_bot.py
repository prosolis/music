"""YouTube bot will run continuously after going live via YouTube"""
import logging
import asyncio
import os
from dotenv import load_dotenv

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from helpers import live_broadcast, live_chat


async def main():
    """Initializes Radio Proslis Bot for YouTube."""
    log_format = '%(asctime)s %(message)s'
    log_level = 10

    logging.basicConfig(format=log_format, level=log_level)
    logger = logging.getLogger('YoutubeBot')
    logger.info("YouTube Bot has started")

    scopes = ["https://www.googleapis.com/auth/youtube.readonly",
              "https://www.googleapis.com/auth/youtube.force-ssl"]

    load_dotenv()
    api_service_name = os.getenv("API_SERVICE_NAME")
    api_version = os.getenv("API_VERSION")
    client_secrets_file = os.getenv("CLIENT_SECRETS_FILE")

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        credentials=credentials)

    live_chat_id = await live_broadcast.get_live_chatid(youtube)

    await live_chat.get_live_chat_messages(youtube, live_chat_id)


if __name__ == "__main__":
    asyncio.run(main())
