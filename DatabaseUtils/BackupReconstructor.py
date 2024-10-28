import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))) 
import logging
from SqlConnector import connect  # Ensure proper path for SqlConnector
from Reconstructor import drop_all_tables, create_tables  # Importing necessary functions from Reconstructor

"""
This script is used to drop all tables from the current database, reconstruct blank tables,
and then insert data from a backup SQL file.
Foreign key constraints will be ignored during the process.
"""

# Function to execute the SQL script from the given backup file
def execute_sql_script(connection, sql_file):
    """Execute the SQL script from the given file while ignoring foreign key constraints."""
    try:
        cursor = connection.cursor()

        # Disable foreign key checks before any operation
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        connection.commit()
        print("Foreign key checks disabled.")

        # Read the SQL file and execute it line by line
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_script = ''
            for line in file:
                sql_script += line
                if line.strip().endswith(';'):  # Full statement reached
                    try:
                        cursor.execute(sql_script)
                        connection.commit()
                        print(f"Executed: {sql_script[:50]}...")  # Feedback
                    except Exception as e:
                        logging.error(f"Error executing statement: {e}")
                        print(f"Error executing statement: {e}")
                    sql_script = ''  # Reset the buffer for the next statement

        # Re-enable foreign key checks after the process is complete
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()
        print("Foreign key checks enabled.")

        cursor.close()
        print(f"Successfully executed: {sql_file}")
    except Exception as e:
        logging.error(f"Error executing {sql_file}: {e}")
        print(f"Error executing {sql_file}: {e}")

# Function to reconstruct the database using the backup file
def reconstruct_database(backup_file):
    """Reconstruct the database by first dropping all tables, recreating blank tables, then inserting data."""
    connection = connect()
    if connection:
        try:
            # Step 1: Drop all tables
            print("Dropping all tables...")
            drop_all_tables(connection)

            # Step 2: Recreate blank tables using Reconstructor.py's 'create_tables'
            print("Recreating blank tables...")
            create_tables()

            # Step 3: Insert data from the backup file
            print(f"Rebuilding database using backup file: {backup_file}")
            execute_sql_script(connection, backup_file)

        except Exception as e:
            print(f"Error during database reconstruction: {e}")
            logging.error(f"Error during database reconstruction: {e}")
        finally:
            connection.close()
            print("MySQL connection closed.")
    else:
        logging.error("Failed to connect to the database.")
        print("Failed to connect to the database.")

# Main function to reconstruct the database from the latest backup
def main():
    # Get the latest backup file from the Backups directory
    project_root = os.path.abspath(os.getcwd())
    backup_folder = os.path.join(project_root, 'Backups')

    # Step 1: Check if backup exists
    backup_files = [f for f in os.listdir(backup_folder) if f.endswith('.sql')]
    if not backup_files:
        print("No backup files found. Exiting.")
        return

    # Step 2: Sort files by modification date (most recent first)
    backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_folder, x)), reverse=True)
    latest_backup_file = os.path.join(backup_folder, backup_files[0])

    print(f"Using latest backup file: {latest_backup_file}")

    # Step 3: Reconstruct the database using the latest backup file
    reconstruct_database(latest_backup_file)

if __name__ == "__main__":
    main()
