# Example GCP Call
from google.cloud.sql.connector import Connector, IPTypes
import yaml
from pydantic import BaseModel
from logger import Logger
from config.settings import settings
import json

class UserDbTyping(BaseModel):
    name: str
    username: str
    password: str
    devices: dict[str, str]
    preferences: list[str]

class UserDbOperations:
    def __init__(self):
        if settings.LOCAL_MODE == 'false':
            self.connector = Connector()

        self.logger_table = "logging.logger_final"

    async def _get_conn(self):
        if settings.LOCAL_MODE == "true":
            import pg8000.dbapi as pgdb
            return pgdb.connect(
                user=settings.USERNAME,
                password=settings.PASSWORD,
                host=settings.PUBLIC_IP,
                port=int(settings.DB_PORT),
                database=settings.DATABASE_NAME
            )
        else:
            return self.connector.connect(
                settings.INSTANCE_CONNECTION_NAME,
                "pg8000",
                db=settings.DATABASE_NAME,
                user=settings.USERNAME,
                password=settings.PASSWORD,
                ip_type=IPTypes.PUBLIC
            )
    
    async def get_device_information(self,username: str) -> tuple[dict[str,str]]:
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            # Device Information is stored in the useres table as a dictionary device_type: apikey
            # There should only be one username in the database, so we can use a simple fetchall
            cursor.execute("SELECT device_type, api_key FROM users.users_staging WHERE username = $1", [username])
            device_information = cursor.fetchall()
            return device_information
        finally:
            # close connection and cursor
            cursor.close()
            conn.close()
    
    async def get_agentic_preferences(self,username: str) -> list[list[str]]:
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            # Preferences will be stored as a list of strings
            cursor.execute("SELECT preferences FROM users.users_staging WHERE username = $1", [username])
            preferences = cursor.fetchone()
            return preferences
        finally:
            cursor.close()
            conn.close()

    async def add_agentic_preference(self,username: str, preference: str) -> str:
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            # Preferences will be stored as a list of strings
            # it would be a preference list - so we need to add it to the list
            cursor.execute("UPDATE users.users_staging SET preferences = preferences || $1 WHERE username = $2", [preference, username])
            conn.commit()
            # close connection
        finally:
            cursor.close()
            conn.close()
        return "Preference added successfully"

    async def remove_agentic_preference(self,username: str, preference: str) -> str:
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            # Preferences will be stored as a list of strings
            # it would be a preference list - so we need to remove it from the list
            cursor.execute("UPDATE users.users_staging SET preferences = array_remove(preferences,$1) WHERE username = $2", [preference, username])
            conn.commit()
        finally:
            # close connection
            cursor.close()
            conn.close()
        return "Preference removed successfully"

    async def get_api_key(self, user_id: str, device_type: str) -> str:
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
        # Get the API key for the user - query via the user_db_call class
            cursor.execute("SELECT devices->$1->>'access_token' FROM users.users_staging WHERE username = $2", [device_type, user_id])
            access_token = cursor.fetchone()
            return access_token[0]
        finally:
            cursor.close()
            conn.close()

    async def log_message(self, logger: Logger) -> tuple[int]:
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            # Log the message to the database
            cursor.execute(f"INSERT INTO {self.logger_table} (timestamp, inference_time, prompt, response, response_metadata, feedback, preferred_response, message_history, system_prompt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", [logger.timestamp, logger.inference_time, json.dumps(logger.prompt), json.dumps(logger.response), json.dumps(logger.response_metadata), logger.feedback, logger.preferred_response, json.dumps(logger.message_history), logger.system_prompt])
            conn.commit()
            id = cursor.fetchone()
            return id
        finally:
            # close connection
            cursor.close()
            conn.close()

    def close_connection(self):
        if self.connector:
            self.connector.close()


# DEV TOOL - ONLY USED FOR TABLE INIT   
def create_user_db_tables():
    with open('../config/gcp_db.yaml', 'r') as file:
        config = yaml.safe_load(file)

    PUBLIC_IP = settings.PUBLIC_IP
    DATABASE_NAME = settings.DATABASE_NAME
    USERNAME = settings.USERNAME
    PASSWORD = settings.PASSWORD
    PORT = settings.DB_PORT

    connector = Connector()

    # Initialize the COnnectino
    conn = connector.connect(
        host=PUBLIC_IP,
        db=DATABASE_NAME,
        user=USERNAME,
        password=PASSWORD,
        port=PORT,
        ip_type=IPTypes.PUBLIC
    )

    cursor = conn.cursor()

    # Create a Schema for the users
    # cursor.execute("CREATE SCHEMA IF NOT EXISTS users")
    # cursor.execute("CREATE TABLE IF NOT EXISTS users.users_staging (id SERIAL PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), preferences TEXT[], devices JSONB, first_name VARCHAR(255), last_name VARCHAR(255))")


    # Create a Schema for Logging
    cursor.execute("CREATE SCHEMA IF NOT EXISTS logging")
    # Create a table for the users
    # Create a table for the logging
    # check the types
    cursor.execute("CREATE TABLE IF NOT EXISTS logging.logger_final (id SERIAL PRIMARY KEY, timestamp TIMESTAMP, inference_time FLOAT, prompt JSONB, response JSONB, response_metadata JSONB, feedback TEXT, preferred_response TEXT, message_history JSONB, system_prompt TEXT)")
    # Commit the changes
    conn.commit()
    conn.close()
    cursor.close()
    return "Tables created successfully"

if __name__ == "__main__":
    create_user_db_tables()
