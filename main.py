from DatabaseUtils.reconstructor import reconstruct_database
from DatabaseUtils.PlayerTableReconstructor import reconstruct_player_table
from Core.Scraper import Scraper

"""
Main script to handle database reconstruction, cleaning player table, and scraping.
"""

if __name__ == "__main__":
    reconstruct_player_table()
    reconstruct_database()



    # Start the scraper after the database and player table have been prepared
    scraper = Scraper()
    scraper.scrape_entire_database()
