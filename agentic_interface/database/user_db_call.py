# Example GCP Call
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import yaml
from pydantic import BaseModel
from logger import Logger
from config.settings import settings
import json
# Create a GCP INSTANCE Class
# Objectives - Operations
# 1. Access Device List
# 2. Access Agentic Preferences

class UserDbTyping(BaseModel):
    name: str
    username: str
    password: str
    devices: dict[str, str]
    preferences: list[str]

class UserDbOperations:
    def __init__(self):
        # Crearte a local version 
        if settings.LOCAL_MODE == "true":
            self.conn = pg8000.connect(
                host=settings.PUBLIC_IP,
                port=settings.DB_PORT,
                user=settings.USERNAME,
                password=settings.PASSWORD,
                database=settings.DATABASE_NAME
            )
        else:
            connector = Connector()

            DATABASE_NAME = settings.DATABASE_NAME
            USERNAME = settings.USERNAME
            PASSWORD = settings.PASSWORD

            self.conn = connector.connect(
                settings.INSTANCE_CONNECTION_NAME,
                "pg8000",
                db=DATABASE_NAME,
                user=USERNAME,
                password=PASSWORD,
                ip_type=IPTypes.PUBLIC
            )

        self.logger_table = "logging.logger_final"
    
    # def upload_user_data(self,user_data: UserDbTyping) -> str:
    #     # psycopq2 will handle the JSONB and ARRAY[VARCHAR(255)] types - so wecan just pass the pydantic model directly
    #     # without any conversions
    #     self.cursor.execute("INSERT INTO users.users_staging (username, password, devices, preferences, first_name, last_name) VALUES (:1, :2, :3, :4, :5, :6)", [user_data.name, user_data.username, user_data.password, user_data.devices, user_data.preferences, user_data.first_name, user_data.last_name])
    #     self.conn.commit()
    #     return "User data uploaded successfully"
    
    def get_device_information(self,username: str) -> tuple[dict[str,str]]:
        cursor = self.conn.cursor()
        # Device Information is stored in the useres table as a dictionary device_type: apikey
        # There should only be one username in the database, so we can use a simple fetchall
        cursor.execute("SELECT device_type, api_key FROM users.users_staging WHERE username = $1", [username])
        device_information = cursor.fetchall()
        return device_information

    
    def get_agentic_preferences(self,username: str) -> tuple[list[str]]:
        print("Getting agentic preferences for username: ", username)
        cursor = self.conn.cursor()
        # Preferences will be stored as a list of strings
        cursor.execute("SELECT preferences FROM users.users_staging WHERE username = $1", [username])
        preferences = cursor.fetchone()
        return preferences

    def add_agentic_preference(self,username: str, preference: str) -> str:
        cursor = self.conn.cursor()
        # Preferences will be stored as a list of strings
        # it would be a preference list - so we need to add it to the list
        cursor.execute("UPDATE users.users_staging SET preferences = preferences || $1 WHERE username = $2", [preference, username])
        self.conn.commit()
        return "Preference added successfully"

    def remove_agentic_preference(self,username: str, preference: str) -> str:
        cursor = self.conn.cursor()
        # Preferences will be stored as a list of strings
        # it would be a preference list - so we need to remove it from the list
        cursor.execute("UPDATE users.users_staging SET preferences = array_remove(preferences,$1) WHERE username = $2", [preference, username])
        self.conn.commit()
        return "Preference removed successfully"

    def get_api_key(self, user_id: str, device_type: str) -> str:
        cursor = self.conn.cursor()
        # Get the API key for the user - query via the user_db_call class
        cursor.execute("SELECT devices->$1->>'access_token' FROM users.users_staging WHERE username = $2", [device_type, user_id])
        access_token = cursor.fetchone()
        return access_token[0]

    def log_message(self, logger: Logger) -> tuple[int]:
        cursor = self.conn.cursor()
        # Log the message to the database
        # need to convert all message history into json
        # json_history = [json.dumps(message) for message in logger.message_history]
        cursor.execute(f"INSERT INTO {self.logger_table} (timestamp, inference_time, prompt, response, response_metadata, feedback, preferred_response, message_history, system_prompt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", [logger.timestamp, logger.inference_time, json.dumps(logger.prompt), json.dumps(logger.response), json.dumps(logger.response_metadata), logger.feedback, logger.preferred_response, json.dumps(logger.message_history), logger.system_prompt])
        self.conn.commit()
        return cursor.fetchone() # return the id of the logged message for feedback column population

    def close_connection(self):
        self.conn.close()


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
