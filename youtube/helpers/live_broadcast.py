"""Modules for interacting with the liveBroadcasts api"""
import logging
import numpy as np

async def get_live_chatid(youtube):
    """Get ChatId from youtube liveBroadcasts api"""
    logger = logging.getLogger('YoutubeProBot')

    try:
        request = youtube.liveBroadcasts().list(
            part="snippet,contentDetails,status",
            broadcastStatus="active",
            broadcastType="all"
        )
        response = request.execute()
        logger.debug("Get LiveBroadcasts list - Success!")

        broadcast_list_size = np.size(response["items"])

        if broadcast_list_size == 0:
            logger.error("YouTube returned 0 broadcasts.")
            return None

        live_chatid = response["items"][0]["snippet"]["liveChatId"]

    except request.HTTPError as request_httperror:
        logger.error(str(request_httperror))
        return None

    return live_chatid
