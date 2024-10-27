import requests
import pandas as pd
import logging

class ScoreFlow:
    """
    This class is responsible for fetching score flow data for a given league and match ID.
    additionally, the class is responsible for processing the score flow data and storing it in a DataFrame.
    """

    def __init__(self, league_id, match_id):
        """
        Initialize the ScoreFlow object with the league ID and match ID.
        
        parameters:
        league_id (int): The ID of the league.
        match_id (int): The ID of the match.
        """

        self.league_id = league_id
        self.match_id = match_id
        self.data = pd.DataFrame()

    # Fetch score flow data for the league
    def fetch_data(self):
        logging.info(f"Fetching score flow data for match {self.match_id} in league {self.league_id}")

        # Fetch score flow data from the Champion Data API
        url = f'https://mc.championdata.com/data/{self.league_id}/{self.match_id}.json'
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code != 200:
            logging.error(f"Failed to retrieve score flow data for match {self.match_id} in league {self.league_id}: {response.status_code}")
            print(f"Failed to retrieve data: {response.status_code}")
            return

        # Parse the JSON response
        json_data = response.json()

        # Access score flow data
        match_stats = json_data.get('matchStats', {})
        score_flow = match_stats.get('scoreFlow', {})

        # Extract score flow data
        scores = score_flow.get('score', [])

        # Check if score flow data is available
        if not scores:
            logging.warning(f"No score flow data found for match {self.match_id} in league {self.league_id}.")
            print(f"No score flow data found for match {self.match_id} in league {self.league_id}.")
            return

        # Create DataFrame from score flow data
        df = pd.DataFrame(scores)
        df['matchId'] = self.match_id

        # Merge with player info if available
        player_info = match_stats.get('playerInfo', {}).get('player', [])
        if player_info:
            players_df = pd.DataFrame(player_info)
            df = pd.merge(
                df,
                players_df[['playerId', 'firstname', 'surname', 'displayName', 'shortDisplayName']],
                how='left',
                on='playerId'
            )
        # Log warning if player info
        else:
            logging.warning(f"Player info not found in score flow data for match {self.match_id} in league {self.league_id}.")
            print(f"Player info not found in score flow data for match {self.match_id} in league {self.league_id}.")

        # Store the data in the object
        self.data = df
        print(f"Fetched {len(df)} score flow records for match {self.match_id}.")
