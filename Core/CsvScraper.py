# CsvScraper.py

import logging
import json
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import re
import traceback
from Utils.Logger import setup_logging
from Utils.JsonLoader import load_json_fields
from Core.LeaguesList import League
from Core.FixtureDetails import Fixture
from Core.MatchDetails import Match
from Core.PeriodData import PeriodData
from Core.ScoreFlowData import ScoreFlow
from Utils.SportCategory import determine_sport_category
from Utils.SanitiseFilename import sanitize_filename
import Utils.CsvHelper as cs  

class CsvScraper:

    """
    This class is responsible for scraping the entire database and saving the data to CSV files.
    This is mostly legacy code, however, it still works if you need to save the data locally into a csv format. 
    The size of all CSV's should be roughly 200MB. 
    """


    def __init__(self):
        # Setup logging with both error and info logs
        self.info_logger, self.error_logger = setup_logging()

        # Load JSON fields for each table
        self.json_fields = load_json_fields()
        self.fixture_fields = self.json_fields['fixture_fields']
        self.match_fields = self.json_fields['match_fields']
        self.period_fields = self.json_fields['period_fields']
        self.score_flow_fields = self.json_fields['score_flow_fields']
        self.player_fields = self.json_fields['player_fields']
        self.squad_fields = self.json_fields['squad_fields']
        self.sport_fields = self.json_fields['sport_fields']

    def scrape_entire_database(self):

        """
        This method scrapes the entire database and saves the data to CSV files.
        """


        sport_id_map = { # Map sport categories to sport IDs
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

        # Iterate over leagues
        for _, league in leagues_df.iterrows():
            league_id = league['id']
            league_name = league['league_season']
            regulation_periods = league['regulationPeriods']
            fixture_id = league['id']
            fixture_title = league['name']
            fixture_year = league['season']
            league_name_and_season = f"{fixture_title} {fixture_year}"

            print(f"\nProcessing fixture {fixture_id} for league '{league_name}'...")

            fixture = Fixture(
                league_id,
                fixture_id, 
                regulation_periods,
                self.info_logger, 
                self.error_logger
                )
            
            fixture.fetch_data()
            print(f"Fetched {len(fixture.data)} fixtures for league {league_id}.")

            if fixture.data.empty:
                print(f"No fixture data available for fixture {fixture_id}.")
                continue

            # Extract squad ids from fixture data
            squad_ids = pd.unique(
                fixture.data[['homeSquadId', 'awaySquadId']].values.ravel()
            ).tolist()
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
            self.info_logger.info(f"Normalized sport category: '{sport_category}' " f"for league: {league_id}")

            # Convert the sport_id_map keys to lowercase
            sport_id_map_lower = {k.lower(): v for k, v in sport_id_map.items()}

            # Check if the sport category exists in the map
            if sport_category_lower in sport_id_map_lower:
                sport_id = sport_id_map_lower[sport_category_lower]
                self.info_logger.info(f"Sport ID found: {sport_id} for category: " f"'{sport_category}'")
            else:
                self.error_logger.error(f"Sport category '{sport_category}' not found in " f"sport_id_map for league {league_id}.")
                sport_id = None  # Skip if category not in map

            # Now sanitize the sport category and league name for file saving
            sanitized_sport_category = sanitize_filename(sport_category)
            sanitized_league_name = sanitize_filename(league_name)

            # Create the league directory
            league_dir = os.path.join("Data", "Leagues", sanitized_sport_category, sanitized_league_name)
            os.makedirs(league_dir, exist_ok=True)

            # Save the fixture CSV
            fixture_csv_path = os.path.join(league_dir, f"{sanitized_league_name} Fixture.csv")
            if not os.path.exists(fixture_csv_path):
                cs.save_fixture_to_csv(fixture.data, fixture_csv_path)
                print(f"Fixture data saved to {fixture_csv_path}")

            match_year = re.search(r'\b(20\d{2})\b', league_name)
            fixture_year = match_year.group(1) if match_year else None

            # Initialize sets to track processed IDs
            processed_unique_match_ids = set()
            processed_unique_squad_ids = set()

            for index, match_row in fixture.data.iterrows():
                if match_row['matchStatus'] in ['scheduled', 'incomplete']:
                    print(f"Skipping match {match_row['matchId']} due to status {match_row['matchStatus']}")
                    continue

                match_id = match_row['matchId'] or 'Unknown'
                fixture.data.at[index, 'sportId'] = sport_id

                # Generate uniqueFixtureId
                uniqueFixtureId = f"{fixture_id}-{match_id}"
                print(f"Unique fixture ID: {uniqueFixtureId}")

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
                }

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
                    self.info_logger.info(f"Generated uniqueSquadId: {uniqueSquadId} " f"for {squad_side} side in match {match_id}.")

                    if uniqueSquadId not in processed_unique_squad_ids:
                        # Save squad info to CSV
                        cs.save_squad_info_to_csv(squad_id, squad_name, fixture_title, str(fixture_year), sport_id)
                        processed_unique_squad_ids.add(uniqueSquadId)

                # Fetch match data
                match = Match(league_id, match_id, fixture_id, sport_id, fixture_year)
                match.fetch_data()

                
                """
                Fetch match data for a given match ID.

                Parameters:
                league_id (int): The ID of the league.
                match_id (int): The ID of the match.
                fixture_id (int): The ID of the fixture.
                sport_id (int): The ID of the sport.
                fixture_year (str): The year of the fixture
                """


                if match.data.empty:
                    self.error_logger.warning(f"Match data is empty for matchId: {match_id}, " f"leagueId: {league_id}.")
                    continue  # Skip to next match

                print(f"Fetched {len(match.data)} match records for " f"match {match_id}.")

                # Ensure 'firstname' and 'surname' are in match.data
                if 'firstname' not in match.data.columns or 'surname' not \
                        in match.data.columns:
                    self.error_logger.error(f"'firstname' or 'surname' not found in match " f"data for matchId: {match_id}. Skipping match.")
                    continue  # Skip this match

                # Process and collect match data
                match_data_list = []
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
                    if not isinstance(firstname, str) or pd.isnull(firstname):
                        firstname = ''
                    else:
                        firstname = firstname.strip()
                    if not isinstance(surname, str) or pd.isnull(surname):
                        surname = ''
                    else:
                        surname = surname.strip()

                    # Check if player_id is missing or invalid
                    if player_id == '0' or not player_id.isdigit():
                        self.error_logger.warning(f"Invalid or missing playerId '{player_id}' " f"for row: {row.to_dict()}")
                        continue  # Skip this row

                    # Log uniquePlayerId
                    uniquePlayerId = f"{player_id}-{squad_id}"
                    self.info_logger.info(f"Generated uniquePlayerId: {uniquePlayerId} for " f"player {player_id} in match {match_id}.")

                    row['matchId'] = str(match_id)
                    row['playerId'] = player_id  # Update playerId
                    row['squadId'] = squad_id
                    row['squadName'] = squad_name

                    # Generate unique IDs
                    uniqueMatchId = f"{match_id}-{player_id}"
                    uniqueSquadId = f"{squad_id}-{squad_name}"

                    row['uniquePlayerId'] = uniquePlayerId
                    row['uniqueMatchId'] = uniqueMatchId
                    row['uniqueSquadId'] = uniqueSquadId

                    match_data_list.append(row.to_dict())

                    # Collect player info
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

                    # Save player info to CSV
                    cs.save_player_info_to_csv(player_info_data)

                print(f"Collected {len(match_data_list)} match entries "
                      f"for league {league_id}.")

                # Save match data to CSV
                match_df = pd.DataFrame(match_data_list)
                match_dir = os.path.join(league_dir, f"Match {match_id}")
                os.makedirs(match_dir, exist_ok=True)
                match_csv_path = os.path.join(match_dir, f"{sanitized_league_name} match {match_id} data.csv")
                match_df.to_csv(match_csv_path, index=False)
                print(f"Match data saved to {match_csv_path}")

                # Save unique fields based on the sport category
                match_fields = match_df.columns if not match_df.empty else []
                cs.save_unique_fields(sanitized_sport_category, match_fields)

                # Create 'Additional Data' directory
                additional_data_dir = os.path.join(match_dir, 'Additional Data')
                os.makedirs(additional_data_dir, exist_ok=True)

                # Fetch period data
                period_data = PeriodData(league_id, match_id)
                period_data.fetch_data()
                print(f"Fetched {len(period_data.data)} period records " f"for match {match_id}.")

                if not period_data.data.empty:
                    # Save period stats to CSV
                    cs.save_period_stats_to_csv(period_data.data, match_id, additional_data_dir, league_name_and_season)

                # Fetch score flow data
                score_flow = ScoreFlow(league_id, match_id)
                score_flow.fetch_data()
                print(f"Fetched {len(score_flow.data)} score flow records "
                      f"for match {match_id}.")

                if not score_flow.data.empty:
                    cs.save_score_flow_to_csv(score_flow.data, league_name_and_season, match_id, additional_data_dir)

                print(f"Completed processing for match {match_id} in league {league_id}.")

            print("Scraping completed.")

if __name__ == "__main__":
    scraper = CsvScraper()
    scraper.scrape_entire_database()
