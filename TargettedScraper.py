import os
import sys

# add the Core and DatabaseUtils directories to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'DatabaseUtils'))

from Core.Scraper import Scraper
from Core.LeaguesList import League
import pandas as pd


"""
This is the main function you execute to extract specific fixture data from the Champion Data API.
This is perfect for testing, as you can specify the fixture IDs you want to test.
Or, you can use this to extract specific fixture data for a given league and fixture ID.

For specific instructions on how to run the scraper, please refer to the README.md file.
"""
def main():
    # Initialize the scraper
    scraper = Scraper()

    # Specify the fixture IDs you want to test
    target_fixture_ids = [10343, 10344, 10064, 10185, 10123, 9923] #TODO Check this website for fixture IDs: https://mc.championdata.com/data/competitions.json

    # Fetch leagues
    leagues_df, _ = League.fetch_leagues()
    print(f"Fetched {len(leagues_df)} leagues.")

    # Filter leagues to only include the ones with fixture IDs in target_fixture_ids
    test_leagues = leagues_df[leagues_df['id'].isin(target_fixture_ids)]

    # Check if test_leagues is empty
    if test_leagues.empty:
        print("No leagues found with the specified fixture IDs.")
        return

    # Run the scraper on the specified fixtures
    for _, league in test_leagues.iterrows():
        league_id = league['id']
        league_name = league['league_season']
        regulation_periods = league['regulationPeriods']
        fixture_id = league['id']

        print(f"\nProcessing fixture {fixture_id} for league '{league_name}'...")

        try:
            # Scrape the fixture data
            scraper.scrape_specific_fixture(league_id, fixture_id, regulation_periods)
        except Exception as e:
            print(f"An error occurred while processing fixture {fixture_id}: {e}")

if __name__ == "__main__":
    main()
