"""postgresproxy provides connectivity and required logic needed to
interactive with the postgres sql database"""
# pylint: disable=too-many-arguments
# pylint: disable=broad-except
import logging
from datetime import datetime, timedelta
import sys
import psycopg2


class PostgresProxy:
    """Class representing proxy connection to Postgres SQL Database"""
    def __init__(self, user, password, database="postgres", host="localhost", port="5432"):
        log_format = '%(asctime)s %(message)s'
        log_level = 10
        logging.basicConfig(format=log_format, level=log_level)
        logger = logging.getLogger('PostgresProxy')

        self._database = database
        self._host = host
        self._user = user
        self._password = password
        self._port = port

        self._conn = self.postgres_connection_open()
        logger.info("Postgres Proxy initialized")

    def postgres_connection_open(self):
        """Connect to Postgres SQL Database"""
        logger = logging.getLogger('PostgresProxy')
        try:
            conn = psycopg2.connect(database=self._database,
                             host=self._host,
                             user=self._user,
                             password=self._password,
                             port=self._port)
        except psycopg2.OperationalError as operation_error:
            self.print_psycopg2_exception(operation_error)
            logger.error("Could not connect to %s database: %s", self._host, operation_error)
            return None

        logger.info("Connection to Postgres SQL Database established")
        return conn

    async def postgres_connection_close(self):
        """Close connection to Postgres SQL Database"""
        logger = logging.getLogger('PostgresProxy')

        self._conn.close()

        logger.info("Connection closed from Postgres SQL Database")

    async def song_likes_command(self, user_id, platform_name, fingerprint):
        """Increment song like record by 1 for a given song"""
        logger = logging.getLogger('PostgresProxy')
        cursor = self._conn.cursor()

        try:
            cursor.execute("""
                SELECT timestamp FROM song_likes 
                WHERE user_id = %s AND platform_name = %s AND song_id =
                    (SELECT song_id FROM song_info WHERE fingerprint = %s)
                ORDER BY timestamp DESC
                LIMIT 1;""", (user_id, platform_name, fingerprint))

            song_likes_row = cursor.fetchone()

            if song_likes_row is not None:
                timestamp_expected = song_likes_row[0] + timedelta(minutes=10)

                if datetime.now() >= timestamp_expected:
                    await self.song_likes_helper(cursor, user_id, platform_name, fingerprint)

            else:
                await self.song_likes_helper(cursor, user_id, platform_name, fingerprint)

            logger.info("Finished insert_song_likes")

        except Exception as error:
            logger.error("Was unable to finsih issue with insert_song_likes: %s", error)
            self.print_psycopg2_exception(error)

        cursor.close()

    async def artist_info_command(self, artist):
        """Query for artist info"""
        logger = logging.getLogger('PostgresProxy')
        cursor = self._conn.cursor()

        try:
            print(artist)
            cursor.execute(""" SELECT youtube, bandcamp, spotify, applemusic FROM artist_info
                               WHERE artist_name = %s """, (artist,))

            artist_info_row = cursor.fetchone()
            logger.info("Finished artist_info_command")
            return artist_info_row

        except Exception as error:
            logger.error("Was unable to finsih issue with artist_info_command: %s", error)
            self.print_psycopg2_exception(error)

        cursor.close()

    async def song_likes_helper(self, cursor, user_id, platform_name, fingerprint):
        """Helper to liminate duplicate code"""
        query = """ UPDATE song_info SET song_likes_count = (song_likes_count + 1)
                    WHERE fingerprint = %s """
        cursor.execute(query, (fingerprint, ))

        query = """ INSERT INTO song_likes VALUES (
                        nextval('song_likes_id_seq'),
                        (SELECT id FROM song_info WHERE fingerprint = %s),
                        %s, %s, DEFAULT) """
        cursor.execute(query, (fingerprint, user_id, platform_name))
        self._conn.commit()

    async def artist_exists(self, artist):
        """Does the given artist already exist inside the DB if not insert the artist"""
        logger = logging.getLogger('PostgresProxy')
        cursor = self._conn.cursor()

        try:
            query = """ SELECT * FROM artist_info WHERE artist_name = %s """;

            cursor.execute(query, (artist, ))
            artist_exists = cursor.fetchone()

            if(artist_exists is None):
                query = """ INSERT INTO artist_info VALUES (
                        nextval('artist_info_id_seq'), %s) """

                cursor.execute(query, (artist, ))
                self._conn.commit()
                logger.info("%s has been added to the database", artist)

            else:
                logger.info("No new artist added")
            

            logger.info("Finished artist_exists")

        except Exception as error:
            logger.error("Was unable to finsih, issue with artist_exists: %s", error)
            self.print_psycopg2_exception(error)

    async def song_exists(self, title, artist, fingerprint):
        """Does the given song already exist inside the DB if not insert the song"""
        logger = logging.getLogger('PostgresProxy')
        cursor = self._conn.cursor()

        try:
            query = """ SELECT * FROM song_info WHERE fingerprint = %s """;

            cursor.execute(query, (fingerprint, ))
            song_exists = cursor.fetchone()

            if(song_exists is None):
                query = """ INSERT INTO song_info VALUES (
                        nextval('song_info_id_seq'), 
                        %s,
                        (SELECT id FROM artist_info WHERE artist_name = %s),
                        %s,
                        DEFAULT) """

                cursor.execute(query, (fingerprint, artist, title))
                self._conn.commit()
                logger.info("%s by %s has been added to the database", title, artist)

            else:
                logger.info("No new song added")
            

            logger.info("Finished song_exists")

        except Exception as error:
            logger.error("Was unable to finsih, issue with song_exists: %s", error)
            self.print_psycopg2_exception(error)

    async def insert_play_history(self, title, artist, fingerprint):
        """insert the song into play history"""
        logger = logging.getLogger('PostgresProxy')
        cursor = self._conn.cursor()

        try:
            query = """ INSERT INTO play_history VALUES (
                        nextval('play_history_id_seq'),
                        (SELECT id FROM song_info WHERE fingerprint = %s),
                        current_timestamp) """;

            cursor.execute(query, (fingerprint, ))

            self._conn.commit()
            logger.info("%s by %s has been record recorded as played", title, artist)            

            logger.info("Finished insert_play_history")

        except Exception as error:
            logger.error("Was unable to finsih, issue with insert_play_history: %s", error)
            self.print_psycopg2_exception(error)

    def print_psycopg2_exception(self, error):
        """Define a function that handles and parses psycopg2 exceptions"""
        # get details about the exception
        logger = logging.getLogger('PostgresProxy')
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno

        # print the connect() error
        print ("\npsycopg2 ERROR:", error, "on line number:", line_num)
        print ("psycopg2 traceback:", traceback, "-- type:", err_type)

        # psycopg2 extensions.Diagnostics object attribute
        print ("\nextensions.Diagnostics:", err_obj)

        # print the pgcode and pgerror exceptions
        print ("pgerror:", error.pgerror)
        print ("pgcode:", error.pgcode, "\n")
        logger.debug("Error Object from postgres: %s", err_obj)
