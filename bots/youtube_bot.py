"""YouTube Bot will run continuously after going live via YouTube"""
import logging
import asyncio
import os
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from helpers import live_chat, live_broadcast


async def main():
    """Initializes Prosolis Radio Bot for YouTube."""
    log_format = '%(asctime)s %(message)s'
    log_level = 30

    logging.basicConfig(filename='youtube_bot.log', filemode='a',
                        level=log_level, format=log_format, encoding="UTF-8")
    logger = logging.getLogger('YoutubeBot')
    logger.info("YouTube Bot has started")
    try:
        youtube = await youtube_authenticate()

        live_chat_id = await live_broadcast.get_live_chatid(youtube)
        print(live_chat_id)

        await live_chat.get_live_chat_messages(youtube, live_chat_id)

    except FileNotFoundError as filenotfounderror:
        logger.error("Was unable to find client_secret_file. Is the path set properly in .env?: %s",
                     filenotfounderror)

async def youtube_authenticate():
    """Capture YouTube for future usage decrease the number of times we need login into the app"""
    logger = logging.getLogger("YoutubeBot")

    scopes = ["https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl"]

    load_dotenv()
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.getenv("CLIENT_SECRETS_FILE")
    credentials = None

    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
            logger.info("Loading the token.pickle")

    # if there are no (valid) credentials availablle, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            logger.info("Using creds to request to access youtube api data")

        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)

            credentials = flow.run_local_server(
                host='localhost',
                port=8088,
                authorization_prompt_message='Please visit this URL: {url}',
                success_message='The auth flow is complete; you may close this window.',
                open_browser=True)

        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build(api_service_name, api_version, credentials=credentials)


if __name__ == "__main__":
    asyncio.run(main())
