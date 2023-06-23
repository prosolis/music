"""postgresproxy provides connectivity and required logic needed to
interactive with the postgres sql database"""
# pylint: disable=too-many-arguments
import logging
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

        conn = self.postgres_connection_open()

        self._cursor = conn.cursor()
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
            logger.error("Could not connect to %s database: %s", self._host, operation_error)
            return None

        logger.info("Connection to Postgres SQL Database established")
        return conn

    async def insert_song_likes(self, title, artist, user_id, platform_name, fingerprint):
        """Increment song like record by 1 for a given song"""
        # logger = logging.getLogger('PostgresProxy')
        # try:
        #    self._cursor()
        print(title, artist, user_id, platform_name, fingerprint)

    async def select_artisit_info(self):
        """Select a given artisit based on a given song. Return an artist object."""
        # logger = logging.getLogger('PostgresProxy')
        return NotImplemented
