import logging
from mysql.connector import Error as mysql_error
import json
import os
import pandas as pd
import re
import traceback
from DatabaseUtils.SqlConnector import connect
from DatabaseUtils.DatabaseHelper import DatabaseHelper
from Utils.Logger import setup_logging
from Utils.JsonLoader import load_json_fields
from Core.LeaguesList import League
from Core.FixtureDetails import Fixture
from Core.MatchDetails import Match
from Core.PeriodData import PeriodData
from Core.ScoreFlowData import ScoreFlow
from Utils.SportCategory import determine_sport_category

"""
This class is responsible for scraping the entire database and updating the data.
It holds basically all of the code that is responsible for scraping the data from the Champion Data API.
All of the supporting classes are imported and used in this class.
For any future work, this class is the one that should be modified and updated. Unless theres critical changes needed in the supporting classes.

Supporting python files:
- LeaguesList
- FixtureDetails
- MatchDetails
- PeriodData
- ScoreFlowData
- SportCategories
- SqlConnector
- JsonLoader
- DatabaseHelper
- Logger


Supporting files:
- Assets/Jsons/leagues_filter.json
- Assets/Jsons/BrokenFixtures.json
- Assets/Jsons/sql_create_queries_file_paths.json
- Assets/Jsons/sql_insert_queries_file_paths.json
- Assets/Jsons/player_info.json
- Assets/Jsons/unique fields / Json files for each table type
- Logs/info.log
- Logs/error.log


SQL files:
- SqlConnector
- Reconstructor
- DatabaseHelper
- Assets/sql create queries
- Assets/sql insert queries

For more information on the methods and how they work, please refer to the documentation in the supporting classes. Or the README.md file.

"""


class Scraper:
    def __init__(self):
        # Setup logging with both error and info logs
        self.info_logger, self.error_logger = setup_logging()

        self.connection = connect()
        if self.connection is None:
            self.error_logger.error("Failed to connect to the database.")
            raise ConnectionError("Database connection failed.")
        self.connection.autocommit = False  # Turn off auto-commit
        self.db_helper = DatabaseHelper(
            self.connection, self.info_logger, self.error_logger)

        # Load JSON fields for each table
        self.json_fields = load_json_fields()
        self.fixture_fields = self.json_fields['fixture_fields']
        self.match_fields = self.json_fields['match_fields']
        self.period_fields = self.json_fields['period_fields']
        self.score_flow_fields = self.json_fields['score_flow_fields']
        self.player_fields = self.json_fields['player_fields']
        self.squad_fields = self.json_fields['squad_fields']
        self.sport_fields = self.json_fields['sport_fields']

        # Path to the BrokenFixtures.json file
        self.broken_fixtures_file = os.path.join('Assets', 'Jsons', 'BrokenFixtures.json')
        # Initialize the broken fixtures list
        self.broken_fixtures = []

        # Load existing broken fixtures if the file exists
        if os.path.exists(self.broken_fixtures_file):
            with open(self.broken_fixtures_file, 'r') as f:
                try:
                    self.broken_fixtures = json.load(f)
                except json.JSONDecodeError:
                    self.broken_fixtures = []

    def add_broken_fixture(self, fixture_id):
        if fixture_id not in self.broken_fixtures:
            self.broken_fixtures.append(fixture_id)
            # Write the updated list to the JSON file
            with open(self.broken_fixtures_file, 'w') as f:
                json.dump(self.broken_fixtures, f)
            self.error_logger.info(f"Added fixtureId {fixture_id} to broken fixtures list.")

    def find_player_id(self, firstname, surname, squad_name=None):
        # Normalize the names
        firstname = firstname.strip().lower()
        surname = surname.strip().lower()
        params = [firstname, surname]

        # Prepare the base query
        query = """
        SELECT playerId FROM static_player_info
        WHERE LOWER(firstname) = %s AND LOWER(surname) = %s
        """

        # If squad_name is provided and not 'Unknown Squad', include it
        if squad_name and squad_name.lower() != 'unknown squad':
            squad_name = squad_name.strip().lower()
            query += " AND LOWER(squadName) = %s"
            params.append(squad_name)

        # Log the query and parameters
        self.error_logger.debug(f"Executing query: {query} with params: {params}")

        # Execute the query
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()

        # Process the result
        if len(result) == 1:
            player_id_found = result[0][0]
            self.error_logger.info(
                f"Found playerId {player_id_found} for {firstname} {surname} with squadName {squad_name}.")
            return player_id_found  # Return the playerId
        elif len(result) > 1:
            self.error_logger.warning(
                f"Multiple playerIds found for {firstname} {surname} with squadName {squad_name}. Using the first one.")
            return result[0][0]
        else:
            self.error_logger.warning(
                f"No playerId found for {firstname} {surname} with squadName {squad_name}.")
            return None  # No match found

    def scrape_entire_database(self):
        # Define the sport_id_map
        sport_id_map = {
            'afl mens': 1,
            'afl womens': 2,
            'nrl mens': 3,
            'nrl womens': 4,
            'fast5 mens': 5,
            'fast5 womens': 6,
            'netball mens': 7,
            'netball womens nz': 8,
            'netball womens australia': 9,
            'netball womens international': 10,
            'netball unknown': 11,
            'nrl unknown': 12
        }

        # Fetch leagues
        leagues_df, _ = League.fetch_leagues()
        print(f"Fetched {len(leagues_df)} leagues.")

        for _, league in leagues_df.iterrows():
            league_id = league['id']
            league_name = league['league_season']
            regulation_periods = league['regulationPeriods']
            fixture_id = league['id']

            print(f"\nProcessing fixture {fixture_id} for league '{league_name}'...")

            self.scrape_specific_fixture(league_id, fixture_id, regulation_periods, sport_id_map)

    def scrape_specific_fixture(self, league_id, fixture_id, regulation_periods, sport_id_map=None):
        if sport_id_map is None:
            # Define the sport_id_map if not provided
            sport_id_map = {
                'afl mens': 1,
                'afl womens': 2,
                'nrl mens': 3,
                'nrl womens': 4,
                'fast5 mens': 5,
                'fast5 womens': 6,
                'netball mens': 7,
                'netball womens nz': 8,
                'netball womens australia': 9,
                'netball womens international': 10,
                'netball unknown': 11,
                'nrl unknown': 12
            }

        league_name = League.get_league_name_and_season(league_id)
        fixture = Fixture(
            league_id, fixture_id, regulation_periods,
            self.info_logger, self.error_logger)
        fixture.fetch_data()
        print(f"Fetched {len(fixture.data)} fixtures for league {league_id}.")

        if fixture.data.empty:
            print(f"No fixture data available for fixture {fixture_id}.")
            return

        # Extract squad ids from fixture data
        squad_ids = pd.unique(fixture.data[['homeSquadId', 'awaySquadId']].values.ravel()).tolist()
        print(f"Extracted squad IDs: {squad_ids}")

        # Filter sport category and sport id
        sport_category, sport_id = determine_sport_category(
            regulation_periods,
            squad_ids,
            league_name,
            league_id
        )

        # Normalize the sport category
        sport_category = sport_category.strip()
        sport_category = re.sub(r'\s+', ' ', sport_category)  # Remove extra spaces
        sport_category_lower = sport_category.lower()

        # Log the normalized category
        self.info_logger.info(f"Normalized sport category: '{sport_category}' for league: {league_id}")

        # Convert the sport_id_map keys to lowercase
        sport_id_map_lower = {k.lower(): v for k, v in sport_id_map.items()}

        # Check if the sport category exists in the map
        if sport_category_lower in sport_id_map_lower:
            sport_id = sport_id_map_lower[sport_category_lower]
            self.info_logger.info(f"Sport ID found: {sport_id} for category: '{sport_category}'")
        else:
            self.error_logger.error(f"Sport category '{sport_category}' not found in sport_id_map for league {league_id}.")
            sport_id = None  # Skip if category not in map

        match_year = re.search(r'\b(20\d{2})\b', league_name)
        fixture_year = match_year.group(1) if match_year else None

        # Start the transaction
        try:
            # Begin transaction
            self.connection.start_transaction()

            # Process sport info
            sport_info_data = {
                'sportId': str(sport_id),
                'sportName': sport_category,
                'fixtureId': str(fixture_id),
                'fixtureTitle': league_name,
                'fixtureYear': fixture_year,
                'uniqueSportId': f"{sport_id}-{fixture_id}"
                if sport_id and fixture_id else 'Unknown'
            }

            # Initialize data structures for batch insertion
            squad_info_list = []
            fixture_data_list = []
            player_info_dict = {}
            match_data_dict = {}
            period_data_dict = {}
            score_flow_data_dict = {}

            # For table names
            table_prefix = sport_category_lower.replace(' ', '_')
            fixture_table = f"{table_prefix}_fixture"
            match_table = f"{table_prefix}_match"
            period_table = f"{table_prefix}_period"
            score_flow_table = f"{table_prefix}_score_flow"

            # Initialize sets to track processed IDs
            processed_unique_match_ids = set()
            processed_unique_squad_ids = set()

            for index, match_row in fixture.data.iterrows():
                if match_row['matchStatus'] in ['scheduled', 'incomplete']:
                    continue

                match_id = match_row['matchId'] or 'Unknown'
                fixture.data.at[index, 'sportId'] = sport_id

                # Generate uniqueFixtureId
                uniqueFixtureId = f"{fixture_id}-{match_id}"

                # Ensure matchName is populated
                match_name = match_row.get('matchName') or (
                    f"{match_row['homeSquadName']} vs "
                    f"{match_row['awaySquadName']} | "
                    f"{match_row['localStartTime']}")

                # Collect fixture data
                fixture_data = {
                    **match_row,
                    'fixtureId': fixture_id,
                    'sportId': sport_id,
                    'matchId': match_id,
                    'uniqueFixtureId': uniqueFixtureId,
                    'matchName': match_name,
                    'uniqueSportId': sport_info_data['uniqueSportId']
                }
                fixture_data_list.append(fixture_data)

                # Collect squad info for both home and away
                for squad_side in ['home', 'away']:
                    squad_id = str(match_row.get(f'{squad_side}SquadId', 'Unknown'))
                    squad_name_raw = match_row.get(f'{squad_side}SquadName', '')

                    # Handle NaN values for squad_name
                    if not isinstance(squad_name_raw, str) or pd.isnull(squad_name_raw):
                        squad_name = 'Unknown Squad'
                    else:
                        squad_name = squad_name_raw.strip()

                    # Generate uniqueSquadId
                    uniqueSquadId = f"{squad_id}-{squad_name}"

                    # Check if uniqueSquadId was processed
                    if uniqueSquadId not in processed_unique_squad_ids:
                        squad_info_data = {
                            'squadId': squad_id,
                            'squadName': squad_name,
                            'uniqueSquadId': uniqueSquadId,
                            'fixtureTitle': sport_info_data['fixtureTitle'],
                            'fixtureYear': sport_info_data['fixtureYear']
                        }
                        squad_info_list.append(squad_info_data)
                        processed_unique_squad_ids.add(uniqueSquadId)

                # Fetch match data
                match = Match(league_id, match_id, fixture_id, sport_id, fixture_year)
                match.fetch_data()

                if match.data.empty:
                    self.error_logger.warning(f"Match data is empty for matchId: {match_id}, leagueId: {league_id}.")
                    continue  # Skip to next match

                print(f"Fetched {len(match.data)} match records for match {match_id}.")

                # Ensure 'firstname' and 'surname' are in match.data
                if 'firstname' not in match.data.columns or 'surname' not in match.data.columns:
                    self.error_logger.error(f"'firstname' or 'surname' not found in match data for matchId: {match_id}. Skipping match.")
                    continue  # Skip this match

                # Process and collect match data
                match_data_list_for_match = []
                for _, row in match.data.iterrows():
                    player_id = str(row.get('playerId', 'Unknown'))
                    squad_id = str(row.get('squadId', 'Unknown'))

                    # Extract squad_name, handle NaN values
                    squad_name_raw = row.get('squadName', '')
                    if not isinstance(squad_name_raw, str) or pd.isnull(squad_name_raw):
                        squad_name = 'Unknown Squad'
                    else:
                        squad_name = squad_name_raw.strip()

                    # Extract firstname and surname
                    firstname = row.get('firstname', '')
                    surname = row.get('surname', '')

                    # Handle non-string types and NaN values
                    firstname = firstname.strip() if isinstance(firstname, str) else ''
                    surname = surname.strip() if isinstance(surname, str) else ''

                    # Check if player_id is missing or invalid
                    if player_id == '0' or not player_id.isdigit():
                        self.error_logger.warning(f"Invalid or missing playerId '{player_id}' for player {firstname} {surname} in match {match_id}.")
                        if firstname and surname:
                            found_player_id = self.find_player_id(firstname, surname, squad_name)
                            if found_player_id:
                                player_id = str(found_player_id)
                            else:
                                self.error_logger.warning(f"Could not find playerId for {firstname} {surname} in match {match_id}. Skipping row.")
                                continue  # Skip this row
                        else:
                            self.error_logger.warning(f"Missing firstname or surname for player in match {match_id}. Skipping row.")
                            continue  # Skip this row

                    uniquePlayerId = f"{player_id}-{squad_id}"

                    row['matchId'] = str(match_id)
                    row['playerId'] = player_id  # Update playerId
                    row['squadId'] = squad_id
                    row['squadName'] = squad_name

                    # Generate unique IDs
                    uniqueMatchId = f"{match_id}-{player_id}"
                    uniqueSquadId = f"{squad_id}-{squad_name}"
                    uniqueSportId = sport_info_data['uniqueSportId']
                    uniqueFixtureId = f"{fixture_id}-{match_id}"

                    row['uniquePlayerId'] = uniquePlayerId
                    row['uniqueMatchId'] = uniqueMatchId
                    row['uniqueSquadId'] = uniqueSquadId
                    row['uniqueSportId'] = uniqueSportId
                    row['uniqueFixtureId'] = uniqueFixtureId

                    match_data_list_for_match.append(row.to_dict())

                    # Add the uniqueMatchId to the set
                    processed_unique_match_ids.add(uniqueMatchId)

                    # Collect player info if not already collected
                    if player_id not in player_info_dict:
                        player_info_data = {
                            'playerId': player_id,
                            'firstname': firstname or 'Unknown',
                            'surname': surname or 'Unknown',
                            'displayName': row.get('displayName', 'Unknown'),
                            'shortDisplayName': row.get('shortDisplayName', 'Unknown'),
                            'squadName': squad_name,
                            'squadId': squad_id,
                            'sportId': sport_id,
                            'uniqueSquadId': uniqueSquadId,
                            'uniquePlayerId': uniquePlayerId
                        }
                        player_info_dict[player_id] = player_info_data

                # Store match data for match_id
                match_data_dict[match_id] = match_data_list_for_match

                # Fetch period data
                period_data = PeriodData(league_id, match_id)
                period_data.fetch_data()

                # Assign matchId to period data
                if not period_data.data.empty:
                    period_data.data['matchId'] = str(match_id)

                # Process and collect period data
                period_data_list_for_match = []
                if not period_data.data.empty:
                    for idx, row in period_data.data.iterrows():
                        period_num = str(row.get('period', 'Unknown'))
                        period_id = f"{match_id}_{period_num}"

                        # Fetch playerId and squadId
                        player_id = str(row.get('playerId', 'Unknown'))
                        squad_id = str(row.get('squadId', 'Unknown'))

                        # Extract squad_name, handle NaN values
                        squad_name_raw = row.get('squadName', '')
                        if not isinstance(squad_name_raw, str) or pd.isnull(squad_name_raw):
                            squad_name = 'Unknown Squad'
                        else:
                            squad_name = squad_name_raw.strip()

                        # Extract firstname and surname
                        firstname = row.get('firstname', '')
                        surname = row.get('surname', '')

                        # Handle non-string types and NaN values
                        firstname = firstname.strip() if isinstance(firstname, str) else ''
                        surname = surname.strip() if isinstance(surname, str) else ''

                        if player_id == '0' or not player_id.isdigit():
                            self.error_logger.warning(f"Invalid or missing playerId '{player_id}' for player {firstname} {surname} in period data for match {match_id}.")
                            if firstname and surname:
                                found_player_id = self.find_player_id(firstname, surname, squad_name)
                                if found_player_id:
                                    player_id = str(found_player_id)
                                else:
                                    self.error_logger.warning(f"Could not find playerId for {firstname} {surname} in period data for match {match_id}. Skipping row.")
                                    continue  # Skip this row
                            else:
                                self.error_logger.warning(f"Missing firstname or surname for player in period data for match {match_id}. Skipping row.")
                                continue  # Skip this row

                        # Generate uniqueMatchId
                        uniqueMatchId = f"{match_id}-{player_id}"

                        # Check if uniqueMatchId was processed
                        if uniqueMatchId not in processed_unique_match_ids:
                            self.error_logger.warning(f"Match data for uniqueMatchId {uniqueMatchId} not found. Skipping period data row.")
                            continue  # Skip this period data row

                        row['playerId'] = player_id
                        row['matchId'] = str(match_id)  # Ensure matchId is assigned

                        # Generate unique IDs
                        uniquePlayerId = f"{player_id}-{squad_id}"
                        uniqueSquadId = f"{squad_id}-{squad_name}"
                        uniqueSportId = sport_info_data['uniqueSportId']
                        uniqueFixtureId = f"{fixture_id}-{match_id}"
                        uniquePeriodId = period_id

                        # Assign IDs back to the row
                        row['uniquePlayerId'] = uniquePlayerId
                        row['uniqueMatchId'] = uniqueMatchId
                        row['uniqueSquadId'] = uniqueSquadId
                        row['uniqueSportId'] = uniqueSportId
                        row['uniqueFixtureId'] = uniqueFixtureId
                        row['periodId'] = period_id
                        row['uniquePeriodId'] = uniquePeriodId

                        # Add the row to the period_data_list_for_match
                        period_data_list_for_match.append(row.to_dict())
                else:
                    self.error_logger.warning(f"No period data for match {match_id}.")

                # Store period data for match_id
                period_data_dict[match_id] = period_data_list_for_match

                # Fetch score flow data
                score_flow = ScoreFlow(league_id, match_id)
                score_flow.fetch_data()

                # Process and collect score flow data
                score_flow_data_list_for_match = []
                if not score_flow.data.empty:
                    score_flow_counter = 1
                    for idx, row in score_flow.data.iterrows():
                        score_flow_id = f"{match_id}_flow_{score_flow_counter}"
                        score_flow_counter += 1

                        # Similar logic for playerId
                        player_id = str(row.get('playerId', 'Unknown'))
                        squad_id = str(row.get('squadId', 'Unknown'))

                        # Extract squad_name, handle NaN values
                        squad_name_raw = row.get('squadName', '')
                        if not isinstance(squad_name_raw, str) or pd.isnull(squad_name_raw):
                            squad_name = 'Unknown Squad'
                        else:
                            squad_name = squad_name_raw.strip()

                        # Extract firstname and surname
                        firstname = row.get('firstname', '')
                        surname = row.get('surname', '')

                        # Handle non-string types and NaN values
                        firstname = firstname.strip() if isinstance(firstname, str) else ''
                        surname = surname.strip() if isinstance(surname, str) else ''

                        if player_id == '0' or not player_id.isdigit():
                            self.error_logger.warning(f"Invalid or missing playerId '{player_id}' for player {firstname} {surname} in score flow data for match {match_id}.")
                            if firstname and surname:
                                found_player_id = self.find_player_id(firstname, surname, squad_name)
                                if found_player_id:
                                    player_id = str(found_player_id)
                                else:
                                    self.error_logger.warning(f"Could not find playerId for {firstname} {surname} in score flow data for match {match_id}. Skipping row.")
                                    continue  # Skip this row
                            else:
                                self.error_logger.warning(f"Missing firstname or surname for player in score flow data for match {match_id}. Skipping row.")
                                continue  # Skip this row

                        # Generate uniqueMatchId
                        uniqueMatchId = f"{match_id}-{player_id}"

                        # Check if uniqueMatchId was processed
                        if uniqueMatchId not in processed_unique_match_ids:
                            self.error_logger.warning(f"Match data for uniqueMatchId {uniqueMatchId} not found. Skipping score flow data row.")
                            continue  # Skip this score flow data row

                        row['playerId'] = player_id
                        row['uniqueMatchId'] = uniqueMatchId
                        row['uniquePlayerId'] = f"{player_id}-{squad_id}"
                        row['scoreFlowId'] = score_flow_id

                        # Generate unique IDs
                        uniqueSquadId = f"{squad_id}-{squad_name}"
                        uniqueSportId = sport_info_data['uniqueSportId']
                        uniqueFixtureId = f"{fixture_id}-{match_id}"

                        row['uniqueSquadId'] = uniqueSquadId
                        row['uniqueSportId'] = uniqueSportId
                        row['uniqueFixtureId'] = uniqueFixtureId

                        score_flow_data_list_for_match.append(row.to_dict())
                else:
                    self.error_logger.warning(f"No score flow data for match {match_id}.")

                # Store score flow data for match_id
                score_flow_data_dict[match_id] = score_flow_data_list_for_match

                # Print statement indicating successful data collection for the match
                print(f"Successfully collected all data for Match {match_id}.")

            print(f"Collected data for fixture {fixture_id}.")

            # Convert player_info_dict.values() to player_info_list
            player_info_list = list(player_info_dict.values())

            # Insert squad info
            try:
                for squad_info_data in squad_info_list:
                    self.db_helper.insert_data_dynamically('squad_info', squad_info_data, self.squad_fields)
                print(f"Inserted {len(squad_info_list)} squad info entries.")
            except mysql_error as err:
                self.error_logger.error(f"Error inserting squad info for fixtureId {fixture_id}: {err.msg}")

            # Insert sport info
            try:
                self.db_helper.insert_data_dynamically('sport_info', sport_info_data, self.sport_fields)
                print(f"Inserted sport info for fixtureId {fixture_id}.")
            except mysql_error as err:
                self.error_logger.error(f"Error inserting sport info for fixtureId {fixture_id}: {err.msg}")
                self.connection.rollback()
                self.add_broken_fixture(fixture_id)
                return  # Exit the method

            # Insert player info
            try:
                for player_info_data in player_info_list:
                    self.db_helper.insert_data_dynamically('player_info', player_info_data, self.player_fields)
                print(f"Inserted {len(player_info_list)} player info entries.")
            except mysql_error as err:
                self.error_logger.error(f"Error inserting player info: {err.msg}")

            # Insert fixture data
            try:
                for fixture_data in fixture_data_list:
                    self.db_helper.insert_data_dynamically(fixture_table, fixture_data, self.fixture_fields)
                print(f"Inserted fixture data for fixture {fixture_id}.")
            except mysql_error as err:
                self.error_logger.error(f"Error inserting fixture data for fixtureId {fixture_id}: {err.msg}")

            # Now, for each match ID, insert match data, period data, score flow data, and print statements
            for match_id in match_data_dict.keys():
                # Insert match data for match_id
                match_data_list_for_match = match_data_dict[match_id]
                try:
                    for match_data in match_data_list_for_match:
                        self.db_helper.insert_data_dynamically(match_table, match_data, self.match_fields)
                    print(f"Inserted match data for match {match_id}.")
                except mysql_error as err:
                    self.error_logger.error(f"Error inserting match data for match {match_id}: {err.msg}")
                    # Continue processing other data

                # Insert period data for match_id
                period_data_list_for_match = period_data_dict.get(match_id, [])
                if period_data_list_for_match:
                    try:
                        for period_row in period_data_list_for_match:
                            self.db_helper.insert_data_dynamically(period_table, period_row, self.period_fields)
                        print(f"Inserted period data for match {match_id}.")
                    except mysql_error as err:
                        self.error_logger.error(f"Error inserting period data for match {match_id}: {err.msg}")
                else:
                    print(f"No period data to insert for match {match_id}.")

                # Insert score flow data for match_id
                score_flow_data_list_for_match = score_flow_data_dict.get(match_id, [])
                if score_flow_data_list_for_match:
                    try:
                        for score_flow_row in score_flow_data_list_for_match:
                            self.db_helper.insert_data_dynamically(score_flow_table, score_flow_row, self.score_flow_fields)
                        print(f"Inserted score flow data for match {match_id}.")
                    except mysql_error as err:
                        self.error_logger.error(f"Error inserting score flow data for match {match_id}: {err.msg}")
                else:
                    print(f"No score flow data to insert for match {match_id}.")

            # Commit the transaction after successful batch insertion
            self.connection.commit()
            print(f"Transaction committed successfully for fixtureId: {fixture_id}")

        except mysql_error as err:
            # Log the error and rollback the transaction
            self.error_logger.error(f"MySQL error during transaction for fixtureId {fixture_id}: {err.msg}")
            self.connection.rollback()
            self.add_broken_fixture(fixture_id)
            return  # Exit the method

        except Exception as e:
            # Log any other exceptions and rollback the transaction
            self.error_logger.error(f"Unexpected error during transaction for fixtureId {fixture_id}: {e}")
            self.error_logger.error(f"Traceback: {traceback.format_exc()}")
            self.connection.rollback()
            self.add_broken_fixture(fixture_id)
            return  # Exit the method

        # At the end, write the broken fixtures list to the JSON file
        with open(self.broken_fixtures_file, 'w') as f:
            json.dump(self.broken_fixtures, f)
