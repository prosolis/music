"""Module providing logging for development and debugging"""
import logging

#channel_id, has_elevated_permissions
async def route_command(youtube, channel_id, has_elevated_permission, text_message):
    """Route in coming command to correct module"""

    logger = logging.getLogger('YoutubeProBot')

    test_command_string = "!test"

    if text_message == test_command_string and has_elevated_permission:
        logger.debug("Found test command")
        await test_command(youtube, channel_id)

async def test_command(youtube, channel_id):
    """Logic for test command, returns message for youtube to send to """
    logger = logging.getLogger('YoutubeProBot')

    try:
        request = youtube.liveChatMessages().insert(
            part="Test Command",
            body={
                "snippet": {
                    "liveChatId": channel_id,
                    "textMessageDetails": {
                    "messageText": "This is a test message from YoutubeProBot"
                    }
                }
            }
        )

        logger.debug("Sent test command response to live stream")

    except request.HTTPError as request_httperror:
        logger.error(str(request_httperror))
