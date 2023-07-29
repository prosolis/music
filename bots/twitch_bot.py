"""Twitch Bot used for interacting with Prosolis Radio stream on Twitch"""
import logging
import os
from dotenv import load_dotenv
from twitchio.ext import commands

from helpers.musicplayer import mpdproxy
from helpers.postgres import postgresproxy


class TwitchBot(commands.Bot):
    """Class for Twitch_Bot extending twitchio bot"""

    # TODO(camcast): #1 Setup log_level as an environment variable
    # TODO(camcast): #2 make one common helper python file for running like, song,
    # artist commands for better maintance

    def __init__(self):
        """Initialise our Bot with our access token, prefix and our channel"""
        log_format = '%(asctime)s %(message)s'
        log_level = 10

        logging.basicConfig(format=log_format, level=log_level)
        self.logger = logging.getLogger('TwitchBot')
        self.logger.info("Twitch Bot has started")

        load_dotenv()
        oauth_token = os.getenv("OAUTH_TOKEN")
        default_channel = os.getenv("DEFAULT_CHANNEL")

        super().__init__(token=oauth_token, prefix='!', initial_channels=[default_channel])

    async def event_ready(self):
        """Notifies us when everything is ready!"""
        self.logger.info("Logged in as | %s", self.nick)
        self.logger.info("User id is | %s", self.user_id)

    async def event_message(self, message):
        """Read all incoming messages execpt response from the bot itself"""

        # Messages with echo set to True are messages sent by the bot
        if message.echo:
            return

        # We must let the bot know we want to handle and invoke our commands
        self.logger.debug(
            "Recieved message from twitch. Author: %s", message.author)
        await self.handle_commands(message)

    @commands.command()
    async def like(self, ctx: commands.Context):
        """Logic for like command, returns a thankful message to twitch chat"""

        mpd = mpdproxy.MPDProxy()
        fingerprint = await mpd.mpd_get_fingerprint()

        load_dotenv()
        platform_name = 'Twitch'
        postgres = postgresproxy.PostgresProxy(
            user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))

        await postgres.song_likes_command(ctx.author.name, platform_name, fingerprint)

        await mpd.mpd_connection_close()
        await postgres.postgres_connection_close()

        return_message = '''Thanks this data will help us continue bringing the
            best music to Prosolis Radio'''

        await ctx.send(return_message)
        self.logger.debug("Sent like command response to twitch stream")

    @commands.command()
    async def song(self, ctx: commands.Context):
        """Logic for song command, returns song title and artist to the twitch chat"""

        mpd = mpdproxy.MPDProxy()
        title, artist = await mpd.mpd_get_current_song_title_and_artist()
        await mpd.mpd_connection_close()

        return_message = f"The current song is {title} by {artist}"

        await ctx.send(return_message)
        self.logger.debug("Sent song command resspone to twitch stream")

    @commands.command()
    async def artist(self, ctx: commands.Context):
        """Logic for artist command, returns artist socials to twitch chat"""
        mpd = mpdproxy.MPDProxy()
        current_artist = await mpd.mpd_get_artist_info()

        load_dotenv()
        postgres = postgresproxy.PostgresProxy(
            user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))
        socials = await postgres.artist_info_command(current_artist)

        await mpd.mpd_connection_close()
        await postgres.postgres_connection_close()

        return_message = f'''Artist Name: {current_artist}
        \n Social Links: '''

        for social in socials:
            if social is not None:
                return_message += f'''{social} \n'''

        await ctx.send(return_message)
        self.logger.debug("Sent artist command resspone to twitch stream")

bot = TwitchBot()
bot.run()
