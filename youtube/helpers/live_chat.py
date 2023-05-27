"""Modules for interacting with the liveChatMessages api"""
import logging
import asyncio

TEST_COMMAND_STRING = "!test"

async def get_live_chat_messages(youtube, live_chatid):
    """Get Youtube Live Chat Messages"""
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

            next_page_token=response["nextPageToken"]
            wait_time = response["pollingIntervalMillis"]/1000
            await asyncio.sleep(wait_time)

    except request.HTTPError as request_httperror:
        logger.error(str(request_httperror))
        return

async def discover_command_requests(youtube, response, live_chatid):
    """Discover any commands passed into live chat"""
    logger = logging.getLogger('YoutubeProBot')

    for items in response["items"]:
        text_message = items["snippet"]["textMessageDetails"]["messageText"]
        is_chat_owner = items["authorDetails"]["isChatOwner"]
        is_chat_moderator = items["authorDetails"]["isChatModerator"]

        if text_message == TEST_COMMAND_STRING and (is_chat_owner or is_chat_moderator):
            logger.debug("Found test command")
            await respond_test_command(youtube, live_chatid)

async def respond_test_command(youtube, live_chatid):
    """Logic for test command, returns test message back to youtube live chat"""
    logger = logging.getLogger('YoutubeProBot')

    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chatid,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                    "messageText": "This is a test message from YoutubeProBot"
                    }
                }
            }
        )
        response = request.execute()
        print(response)
        logger.debug("Sent test command response to live stream")

    except request.HTTPError as request_httperror:
        logger.error(str(request_httperror))
