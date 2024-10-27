import os
import pandas as pd
from Utils.SanitiseFilename import sanitize_filename




def ensure_directory_exists(directory_path):
    """
    Ensure the directory exists. If it doesn't, create it.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def save_dataframe_to_csv(df, file_path, force_save=False):
    """
    Save a pandas DataFrame to a CSV file.

    Parameters:
    df (pandas.DataFrame): The DataFrame to save.
    file_path (str): The full path where the CSV should be saved.
    force_save (bool): If True, the file will be overwritten regardless of existing data.
    """
    if os.path.exists(file_path) and not force_save:
        print(f"File already exists: {file_path}. Skipping save.")
    else:
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")

def save_fixture_to_csv(fixture_data, fixture_csv_path):
    """
    Save fixture data to a CSV file.

    Parameters:
    fixture_data (pandas.DataFrame): The DataFrame containing fixture data.
    fixture_csv_path (str): The path where the fixture CSV should be saved.
    """
    ensure_directory_exists(os.path.dirname(fixture_csv_path))
    save_dataframe_to_csv(fixture_data, fixture_csv_path, force_save=True)

def save_score_flow_to_csv(score_flow_data, league_name_and_season, match_id, match_dir):
    """
    Save score flow data to a CSV file.

    Parameters:
    score_flow_data (pandas.DataFrame): The DataFrame containing score flow data.
    league_name_and_season (str): The sanitized league name and season, used to generate the file name.
    match_id (int): The ID of the match, used to generate the file name.
    match_dir (str): The directory where the CSV file will be saved.
    """
    ensure_directory_exists(match_dir)
    clean_league_name = sanitize_filename(league_name_and_season)  # Use the sanitize_filename function
    file_name = f'{clean_league_name} match {match_id} score flow.csv'
    output_csv_path = os.path.join(match_dir, file_name)

    save_dataframe_to_csv(score_flow_data, output_csv_path, force_save=True)

def save_period_stats_to_csv(df, match_id, additional_data_dir, league_name_and_season):
    """
    Save period stats to individual CSV files based on the period.
    Ensure that the period files do not have redundant year names.
    """
    ensure_directory_exists(additional_data_dir)
    if 'period' in df.columns:
        periods = df['period'].unique()
        clean_league_name = sanitize_filename(league_name_and_season)  # Use the sanitize_filename function

        for i, period in enumerate(periods, start=1):
            period_df = df[df['period'] == period].copy()
            period_df['matchId'] = match_id
            period_df['periodId'] = i

            # Ensure the period filename has a clean format, without duplicating the year
            # Format: {clean_league_name} match {match_id} period {i} details.csv
            output_csv_path = os.path.join(additional_data_dir, f'{clean_league_name} match {match_id} period {i} details.csv')

            save_dataframe_to_csv(period_df, output_csv_path)
    else:
        print(f"No 'period' data available for match {match_id}.")

def save_unique_fields(sport_category, match_fields):
    """
    Save unique fields to a CSV file based on the sport category.
    """
    misc_csv_dir = os.path.join("Data", "misc csv files")
    ensure_directory_exists(misc_csv_dir)

    unique_fields_csv = os.path.join(misc_csv_dir, f'unique fields {sport_category}.csv')

    if os.path.exists(unique_fields_csv):
        existing_fields_df = pd.read_csv(unique_fields_csv)
        existing_fields = set(existing_fields_df['Field'])
    else:
        existing_fields = set()
        existing_fields_df = pd.DataFrame(columns=['Field'])

    new_fields = set(match_fields) - existing_fields

    if new_fields:
        new_fields_df = pd.DataFrame(new_fields, columns=['Field'])
        updated_df = pd.concat([existing_fields_df, new_fields_df], ignore_index=True)
        updated_df.to_csv(unique_fields_csv, index=False)
        print(f"Added {len(new_fields)} new fields to {unique_fields_csv}")

def save_squad_info_to_csv(squad_id, squad_name, fixture_title, fixture_year, sport_id):
    """
    Save squad information to a CSV file in the 'misc csv files' directory, but only for women's netball (sport_id 8, 9, or 10).

    Parameters:
    squad_id (int): The ID of the squad.
    squad_name (str): The name of the squad.
    fixture_title (str): The title of the fixture.
    fixture_year (str): The year of the fixture.
    sport_id (int): The ID of the sport (used to filter relevant squads).
    """

    # Check
    misc_csv_dir = os.path.join("Data", "misc csv files")
    ensure_directory_exists(misc_csv_dir)

    csv_file_path = os.path.join(misc_csv_dir, 'squad_info.csv')

    # Check if the CSV file exists; if not, create an empty DataFrame with the required columns
    if os.path.exists(csv_file_path):
        squad_df = pd.read_csv(csv_file_path)
    else:
        squad_df = pd.DataFrame(columns=['SquadID', 'SquadName', 'FixtureTitle', 'FixtureYear', 'SportID'])

    # Create a new entry DataFrame
    new_entry = pd.DataFrame([[squad_id, squad_name, fixture_title, fixture_year, sport_id]],
                             columns=['SquadID', 'SquadName', 'FixtureTitle', 'FixtureYear', 'SportID'])

    # Concatenate the new entry with the existing DataFrame
    squad_df = pd.concat([squad_df, new_entry], ignore_index=True)

    # Remove any duplicate rows (ensure uniqueness across all columns)
    squad_df = squad_df.drop_duplicates(subset=['SquadID', 'SquadName', 'FixtureTitle', 'FixtureYear', 'SportID'], keep='first')

    # Save the updated DataFrame back to the CSV file
    squad_df.to_csv(csv_file_path, index=False)
    print(f"Squad info updated and saved to {csv_file_path}")

def save_player_info_to_csv(player_info_data):
    """
    Save player information to a CSV file in the 'misc csv files' directory.

    Parameters:
    player_info_data (dict): A dictionary containing player information.
    """
    misc_csv_dir = os.path.join("Data", "misc csv files")
    ensure_directory_exists(misc_csv_dir)

    csv_file_path = os.path.join(misc_csv_dir, 'player_info.csv')

    # Check if the CSV file exists; if not, create an empty DataFrame with the required columns
    if os.path.exists(csv_file_path):
        player_df = pd.read_csv(csv_file_path)
    else:
        player_df = pd.DataFrame(columns=['playerId', 'firstname', 'surname', 'displayName', 'shortDisplayName', 'squadName', 'squadId', 'sportId', 'uniqueSquadId', 'uniquePlayerId'])

    # Create a new entry DataFrame
    new_entry = pd.DataFrame([player_info_data])

    # Concatenate the new entry with the existing DataFrame
    player_df = pd.concat([player_df, new_entry], ignore_index=True)

    # Remove any duplicate rows based on 'playerId' and 'squadId'
    player_df = player_df.drop_duplicates(subset=['playerId', 'squadId'], keep='first')

    # Save the updated DataFrame back to the CSV file
    player_df.to_csv(csv_file_path, index=False)
    print(f"Player info updated and saved to {csv_file_path}")
