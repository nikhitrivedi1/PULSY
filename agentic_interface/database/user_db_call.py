"""
Database Operations for Agent Backend

Handles PostgreSQL operations for:
- User preferences and goals
- Device information (API keys)
- Conversation logging
- Feedback storage

Connection Management:
- LOCAL_MODE=true: Direct TCP connection to PostgreSQL
- LOCAL_MODE=false: Google Cloud SQL Connector with IAM auth

Uses pg8000 as the PostgreSQL driver (compatible with Cloud SQL Connector).

Security Note: API keys are stored encrypted in database but passed
              plainly to agent context. Future work should use secure vaults.
"""

from google.cloud.sql.connector import Connector, IPTypes
from pydantic import BaseModel
from logger import Logger
from config.settings import settings
import json

class UserDbTyping(BaseModel):
    """Type definition for user data structure"""
    name: str
    username: str
    password: str
    devices: dict[str, str]  # device_type: api_key
    preferences: list[str]

class UserDbOperations:
    """
    Database operations for agent backend
    
    Provides async methods for:
    - Fetching user preferences and device info
    - Logging conversations
    - Storing feedback
    
    Automatically handles connection management based on LOCAL_MODE setting.
    """
    
    def __init__(self):
        """
        Initialize database connection
        
        If running in production (LOCAL_MODE=false), creates Cloud SQL Connector.
        If running locally (LOCAL_MODE=true), uses direct TCP connection.
        """
        if settings.LOCAL_MODE == 'false':
            self.connector = Connector()  # Google Cloud SQL Connector

        # Database table for conversation logs
        self.logger_table = "logging.logger_final"
        self.eval_table = "logging.eval_final"

    async def _get_conn(self):
        """
        Establish database connection based on environment
        
        Returns:
            pg8000 connection object
        
        Note: Connections should be closed after use to avoid connection pool exhaustion
        """
        if settings.LOCAL_MODE == "true":
            # Local development: Direct TCP connection
            import pg8000.dbapi as pgdb
            return pgdb.connect(
                user=settings.DB_USERNAME,
                password=settings.PASSWORD,
                host=settings.PUBLIC_IP,
                port=int(settings.DB_PORT),
                database=settings.DATABASE_NAME
            )
        else:
            # Production: Cloud SQL Connector with IAM auth
            return self.connector.connect(
                settings.INSTANCE_CONNECTION_NAME,
                "pg8000",
                db=settings.DATABASE_NAME,
                user=settings.USERNAME,
                password=settings.PASSWORD,
                ip_type=IPTypes.PUBLIC
            )
    
    async def get_device_information(self, username: str) -> tuple[dict[str, str]]:
        """
        Retrieve user's connected wearable devices and API keys
        
        Args:
            username: User's username
        
        Returns:
            tuple: List of (device_type, api_key) tuples for all user devices
        
        Example:
            [('Oura Ring', 'ABC123...'), ('Apple Watch', 'XYZ789...')]
        """
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT device_type, api_key FROM users.users_staging WHERE username = $1", 
                [username]
            )
            device_information = cursor.fetchall()
            return device_information
        finally:
            cursor.close()
            conn.close()
    
    async def get_agentic_preferences(self, username: str) -> list[list[str]]:
        """
        Fetch user's health preferences for personalized responses
        
        Preferences might include:
        - Preferred metrics to track
        - Health goals
        - Communication style preferences
        
        Args:
            username: User's username
        
        Returns:
            list: Nested list containing user preferences
                 Returns None if user has no preferences set
        """
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT preferences FROM users.users_staging WHERE username = $1", 
                [username]
            )
            preferences = cursor.fetchone()
            return preferences
        finally:
            cursor.close()
            conn.close()

    async def add_agentic_preference(self, username: str, preference: str) -> str:
        """
        Add a new preference to user's profile
        
        Uses PostgreSQL array concatenation (||) to append to existing list.
        
        Args:
            username: User's username
            preference: New preference to add
        
        Returns:
            str: Success message
        """
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users.users_staging SET preferences = preferences || $1 WHERE username = $2", 
                [preference, username]
            )
            conn.commit()
            return "Preference added successfully"
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

    async def log_message(self, logger: Logger, eval_mode: bool = False) -> tuple[int]:
        if eval_mode:
            table = self.eval_table
        else:
            table = self.logger_table
        conn = await self._get_conn()
        cursor = conn.cursor()
        try:
            # Log the message to the database
            cursor.execute(f"INSERT INTO {table} (timestamp, inference_time, prompt, response, response_metadata, feedback, preferred_response, message_history, system_prompt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", [logger.timestamp, logger.inference_time, json.dumps(logger.prompt), json.dumps(logger.response), json.dumps(logger.response_metadata), logger.feedback, logger.preferred_response, json.dumps(logger.message_history), logger.system_prompt])
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
