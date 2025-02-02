import json
import sys
import os


# test for file name


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from DatabaseUtils.SqlConnector import connect
import logging

"""
This script is used to drop all tables from the current database and create new tables by executing SQL scripts.
Perfect for reconstructing the database schema and testing the SQL scripts.

For specific instructions on how to run the script, please refer to the README.md file.
"""

# Function to drop all tables from the current database
def drop_all_tables(connection):
    """Drop all tables from the current database, including those with foreign key constraints."""
    try:
        cursor = connection.cursor()

        # Disable foreign key checks before dropping the tables
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        print("Foreign key checks disabled.")

        # Query to get all table names
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        # Drop each table, except for 'static_player_info'
        for table in tables:
            table_name = table[0]
            drop_table_query = f"DROP TABLE IF EXISTS `{table_name}`;"
            cursor.execute(drop_table_query)
            print(f"Dropped table: {table_name}")


        # Re-enable foreign key checks after dropping the tables
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Foreign key checks enabled.")

        # Commit the changes and close the cursor
        connection.commit()
        cursor.close()
        print("Successfully dropped all tables.")
    except Exception as e:
        logging.error(f"Error dropping tables: {e}")
        print(f"Error dropping tables: {e}")

# Function to select the database before executing any SQL commands
def select_database(connection, db_name):
    """Select the database before executing any SQL commands."""
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE `{db_name}`;")
        print(f"Database selected: {db_name}")
    except Exception as e:
        logging.error(f"Error selecting database: {e}")
        print(f"Error selecting database: {e}")

# Function to execute the SQL script from the given file
def execute_sql_script(connection, sql_file):
    """Execute the SQL script from the given file to create tables."""
    try:
        with open(sql_file, 'r') as file:
            sql_script = file.read()

        cursor = connection.cursor()
        for result in cursor.execute(sql_script, multi=True):
            if result.with_rows:
                print(f"Executed a statement from {sql_file}: {result.statement}")
        print(f"Successfully executed: {sql_file}")
        cursor.close()
    except Exception as e:
        logging.error(f"Error executing {sql_file}: {e}")
        print(f"Error executing {sql_file}: {e}")

# Function to create tables by executing SQL scripts
def create_tables():
    """Read the sql_file_paths.json and execute each SQL script to create tables."""
    try:
        with open('Assets/jsons/sql_create_queries_file_paths.json', 'r') as json_file:
            sport_sql_files = json.load(json_file)

        connection = connect()

        # Check if the connection is successful
        if connection:
            # Select the PowerData database
            select_database(connection, 'PowerData')

            # Execute the SQL scripts for each sport
            for sport, sql_files in sport_sql_files.items():
                print(f"Creating tables for {sport}...")
                for category, sql_file in sql_files.items():
                    if os.path.exists(sql_file):
                        print(f"Executing {category}: {sql_file}")
                        execute_sql_script(connection, sql_file)
                    else:
                        print(f"SQL file not found: {sql_file}")

            connection.close()
        else:
            logging.error("Failed to connect to the database.")
            print("Failed to connect to the database.")
    except Exception as e:
        logging.error(f"Error in create_tables: {e}")
        print(f"Error in create_tables: {e}")

def reconstruct_database():
    """Function to drop all tables and recreate them by executing SQL scripts."""
    connection = connect()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("USE `PowerData`;")
            cursor.close()
            drop_all_tables(connection)
            create_tables()
        except Exception as e:
            print(f"Error reconstructing the database: {e}")
        finally:
            connection.close()
    else:
        logging.error("Failed to connect to the database.")
        print("Failed to connect to the database.")


if __name__ == "__main__":
    reconstruct_database()
