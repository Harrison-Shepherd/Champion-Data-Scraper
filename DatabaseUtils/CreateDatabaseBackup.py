import os
from datetime import datetime
from SqlConnector import connect  



"""
Creates a backup of the powerdata database and stores it in the '/Backups' folder at the root level.
This version uses Python's mysql-connector to handle the entire process without external utilities.

This is useful because it allows you to create a backup of the database without relying on external utilities.
It also provides more control over the backup process and allows you to customize the backup file name and location.
"""

def create_backup():
    try:
        # Connect to the database
        connection = connect()
        if connection is None:
            print("Connection to the database failed. Backup cannot be created.")
            return

        cursor = connection.cursor()

        project_root = os.path.abspath(os.getcwd())
        
        # Define the path for the 'Backups' folder within the root project folder
        backup_folder = os.path.join(project_root, 'Backups')
        
        # Create 'Backups' folder at the root level if it doesn't exist
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # Define the backup file name with a timestamp (DD-MM-YYYY - time AM/PM.sql)
        # Replace the ':' with a '-' to make it a valid file name
        timestamp = datetime.now().strftime('%d-%m-%Y - %I-%M%p')
        backup_file = os.path.join(backup_folder, f'powerdata_backup_{timestamp}.sql')

        # Open the backup file with utf-8 encoding to handle all characters
        with open(backup_file, 'w', encoding='utf-8') as f:
            # Write SQL statements to the backup file

            # Backup schema (create table statements)
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            for (table_name,) in tables:
                # Write CREATE TABLE statement for each table
                cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_table_stmt = cursor.fetchone()[1]
                f.write(f"\n-- Table structure for `{table_name}`\n")
                f.write(f"{create_table_stmt};\n\n")

                # Backup table data (insert statements)
                cursor.execute(f"SELECT * FROM `{table_name}`")
                rows = cursor.fetchall()
                if rows:
                    columns_query = f"SHOW COLUMNS FROM `{table_name}`"
                    cursor.execute(columns_query)
                    column_names = [col[0] for col in cursor.fetchall()]

                    f.write(f"-- Dumping data for table `{table_name}`\n")
                    for row in rows:
                        values = ', '.join(f"'{{}}'".format(str(value).replace("'", "''")) if value is not None else 'NULL' for value in row)
                        insert_stmt = f"INSERT INTO `{table_name}` ({', '.join(column_names)}) VALUES ({values});"
                        f.write(f"{insert_stmt}\n")

            print(f"Backup created successfully at {backup_file}")

    except Exception as e:
        print(f"Error occurred while creating backup: {e}")
    finally:
        # Ensure the connection is properly closed
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    create_backup()
