import sys
import os
import json
from DatabaseUtils.SqlConnector import connect
from mysql.connector import Error

JSON_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Assets', 'Jsons', 'player_info.json'))

"""
This script provides three functions:
1. clean_static_player_info_table: Cleans the static_player_info table by truncating it.
2. create_static_player_info_table: Creates the static_player_info table if it doesn't exist.
3. insert_data_from_json_into_static_player_info: Inserts player data from a JSON file into the static_player_info table.
"""

# Function to clean the static_player_info table
def clean_static_player_info_table():
    """Cleans the static_player_info table by truncating it."""
    try:
        connection = connect()
        if connection:
            cursor = connection.cursor()
            query = "TRUNCATE TABLE static_player_info"
            cursor.execute(query)
            connection.commit()
            print("Table 'static_player_info' has been successfully cleaned.")
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    except Error as e:
        print(f"Error occurred: {e}")

# Function to create the static_player_info table
def create_static_player_info_table():
    """Creates the static_player_info table if it doesn't exist."""
    try:
        connection = connect()
        if connection:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS static_player_info (
                playerId BIGINT PRIMARY KEY,
                firstname VARCHAR(255),
                surname VARCHAR(255),
                displayName VARCHAR(255),
                shortDisplayName VARCHAR(255),
                squadName VARCHAR(255),
                squadId INT,
                sportId INT,
                uniqueSquadId VARCHAR(255),
                uniquePlayerId VARCHAR(255)
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'static_player_info' has been successfully created.")
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    except Error as e:
        print(f"Error occurred while creating the table: {e}")

# Function to insert data from JSON into the static_player_info table
def insert_data_from_json_into_static_player_info():
    """Inserts data from JSON into static_player_info table."""
    try:
        connection = connect()
        if connection:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO static_player_info (playerId, firstname, surname, displayName, shortDisplayName, squadName, squadId, sportId, uniqueSquadId, uniquePlayerId)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                firstname=VALUES(firstname), 
                surname=VALUES(surname), 
                displayName=VALUES(displayName),
                shortDisplayName=VALUES(shortDisplayName),
                squadName=VALUES(squadName),
                squadId=VALUES(squadId),
                sportId=VALUES(sportId),
                uniqueSquadId=VALUES(uniqueSquadId),
                uniquePlayerId=VALUES(uniquePlayerId);
            """
            with open(JSON_FILE_PATH, 'r') as file:
                for line in file:
                    player = json.loads(line.strip())
                    data = (
                        player.get('playerId'),
                        player.get('firstname'),
                        player.get('surname'),
                        player.get('displayName'),
                        player.get('shortDisplayName'),
                        player.get('squadName'),
                        player.get('squadId'),
                        player.get('sportId'),
                        player.get('uniqueSquadId'),
                        player.get('uniquePlayerId')
                    )
                    cursor.execute(insert_query, data)
            connection.commit()
            print("Data has been successfully inserted into 'static_player_info'.")
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    except Error as e:
        print(f"Error occurred: {e}")
    except json.JSONDecodeError as je:
        print(f"Error decoding JSON: {je}")

# Function to clean, create, and insert data into static_player_info table
def reconstruct_player_table():
    """Cleans the static_player_info table, creates it if necessary, and inserts data from the JSON file."""
    clean_static_player_info_table()
    create_static_player_info_table()
    insert_data_from_json_into_static_player_info()

if __name__ == "__main__":
    reconstruct_player_table()
