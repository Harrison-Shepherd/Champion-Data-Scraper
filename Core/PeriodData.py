import requests
import pandas as pd
import logging

class PeriodData:
    """
    This class is responsible for fetching period stats for a given league and match ID.
    Additionally, the class is responsible for processing the period data and storing it in a DataFrame.
    """
    def __init__(self, league_id, match_id):
        """
        Initialize the PeriodData object with the league ID and match ID.

        Parameters:
        league_id (int): The ID of the league.
        match_id (int): The ID of the match.
        """

        self.league_id = league_id
        self.match_id = str(match_id)
        self.data = pd.DataFrame()


    # Fetch period stats for the league
    def fetch_data(self):
        logging.info(f"Fetching period stats for match {self.match_id} in league {self.league_id}")

        # Fetch period data from the Champion Data API
        url = f'https://mc.championdata.com/data/{self.league_id}/{self.match_id}.json'
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code != 200:
            logging.error(f"Failed to retrieve data for match {self.match_id} in league {self.league_id}: {response.status_code}")
            return

        # Parse the JSON response
        json_data = response.json()

        # Access player period stats
        match_stats = json_data.get('matchStats', {})
        player_period_stats = match_stats.get('playerPeriodStats', {})

        # Extract player period stats
        players = player_period_stats.get('player', [])

        # Check if player period stats are available
        if not players:
            logging.warning(f"No player period stats found for match {self.match_id} in league {self.league_id}.")
            print(f"No player period stats found for match {self.match_id} in league {self.league_id}.")
            return

        # Create DataFrame from player period stats
        df = pd.DataFrame(players)

        # Merge with player info if available
        player_info = match_stats.get('playerInfo', {}).get('player', [])
        if player_info:
            players_info_df = pd.DataFrame(player_info)
            df = pd.merge(
                df,
                players_info_df[['playerId', 'firstname', 'surname', 'displayName', 'shortDisplayName']],
                how='left',
                on='playerId'
            )
        # Log warning if player info not found
        else:
            logging.warning(f"Player info not found in period data for match {self.match_id} in league {self.league_id}.")
            print(f"Player info not found in period data for match {self.match_id} in league {self.league_id}.")

        # Generate uniquePeriodId
        df['uniquePeriodId'] = df.apply(
            lambda row: f"{row['period']}-{row['playerId']}" if pd.notnull(row.get('period')) and pd.notnull(row.get('playerId')) else 'Unknown',
            axis=1
        )

        # Log the number of period records fetched
        self.data = df
        print(f"Fetched {len(df)} period records for match {self.match_id}.")
