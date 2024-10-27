
# Champion Data Scraper

## Table of Contents
- [Introduction](#introduction)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Structure](#Project-Structure)
- [Modules and Components](#modules-and-components)
- [Core Modules](#core-modules)
- [Utils Modules](#utils-modules)
- [Database Schema](#database-schema)
- [Tables and Fields](#tables-and-fields)
- [Relationships](#relationships)
- [Data Flow](#data-flow)
- [Error Handling and Logging](#error-handling-and-logging)
- [Extending the Project](#extending-the-project)
- [Known Issues and Considerations](#known-issues-and-considerations)
- [Conclusion](#conclusion)

## Introduction
The Champion Data Scraper is a comprehensive Python project designed to scrape sports data from the Champion Data API, process it, and store it in a MySQL database. The data includes leagues, fixtures, match details, period data, and score flow data. This project is intended for data analysts, sports statisticians, and developers who need access to detailed sports data for analysis, reporting, or further processing.

This documentation provides an in-depth guide to the project's structure, functionality, and usage, enabling new developers or users to understand, maintain, and extend the project effectively.

## Project Overview
The project connects to the Champion Data API to retrieve sports data across various leagues and matches. It processes the data, handles exceptions, and stores the information in a structured MySQL database.

Key features include:
- Dynamic data fetching and processing for multiple leagues and sports.
- Comprehensive error handling and logging mechanisms.
- Modular design with clear separation of concerns.
- Ability to extend and customize for additional sports or data types.

## Architecture
The project follows a modular architecture, separating core functionalities into distinct modules and utilities. The main scraper orchestrates the data fetching and processing, utilizing helper classes and functions for specific tasks.

> **Note**: Include an architecture diagram if possible.

## Setup and Installation

### Prerequisites
- Python 3.6 or higher
- MySQL Server (with appropriate user permissions)
- Required Python packages (listed in requirements.txt)

### Installation Steps

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/champion-data-scraper.git
    cd champion-data-scraper
    ```

2. **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Required Packages**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up MySQL Database**
    - Create a new MySQL database for the project.
    - Ensure the user has the necessary permissions.
    - Update the database connection settings in `DatabaseUtils/SqlConnector.py`.

5. **Run Database Initialization Scripts**
    - Execute SQL scripts located in `Assets/sql create queries/` to create the necessary tables.
    - These scripts define the database schema required by the scraper.

## Configuration

### Database Connection
Update the `DatabaseUtils/SqlConnector.py` file with your MySQL connection details:
```python
def connect():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='your_database_name',
            user='your_username',
            password='your_password'
        )
        return connection
    except mysql.connector.Error as e:
        # Handle connection error
        return None
```

### Logging Configuration
Logging is configured in `Utils/Logger.py`. By default, logs are saved in the `Logs` directory:
- `info.log`: General information about the scraping process.
- `error.log`: Detailed error messages and exceptions.
You can adjust the logging levels and formats as needed.

### JSON Configurations
The project uses several JSON files located in `Assets/Jsons/` for configurations:
- `leagues_filter.json`: Contains filtering rules for leagues and sports categorization.
- `BrokenFixtures.json`: Keeps track of fixtures that encountered errors during processing.
- Other JSON files define field mappings and SQL query templates.

## Usage

### Running the Scraper
To start the scraping process:
```bash
python Main.py
python CsvScraper.py
python TestScraper.py
```
This will:
- Connect to the MySQL database.
- Fetch all available leagues.
- Iterate through each league and process fixtures, matches, period data, and score flow data.
- Insert the processed data into the appropriate database tables.

### Command-Line Arguments (Optional)
You can modify `Scraper.py` to accept command-line arguments for more control, such as specifying a particular league or fixture to process.
For a solution right now, use TestScraper.py.

## Modules and Components

## Program Structure


```bash
├CHAMPION DATA SCRAPER
├── Assets
│   └── jsons
│       ├── unique fields
│       ├── BrokenFixtures.json
│       ├── leagues_filter.json
│       ├── player_info.json
│       ├── sql_create_queries_file_paths.json
│       └── sql_insert_queries_file_paths.json
│       └── sql create queries                                   # Fixture, Match, Period, Scoreflow in each
│           ├── AFL Mens
│           ├── AFL Womens
│           ├── fast5 mens
│           ├── fast5 womens
│           ├── Netball Australian Womens
│           ├── Netball International Womens
│           ├── Netball Mens
│           ├── Netball NZ Womens
│           ├── NRL Mens
│           ├── NRL Womens
│           ├── Players
│           ├── Sports
│           └── Squads
│       └── sql insert queries                                  # Fixture, Match, Period, Scoreflow in each
│           ├── AFL Mens
│           ├── AFL Womens
│           ├── fast5 mens
│           ├── fast5 womens
│           ├── Netball Australian Womens
│           ├── Netball International Womens
│           ├── Netball Mens
│           ├── Netball NZ Womens
│           ├── NRL Mens
│           ├── NRL Womens
│           ├── Players
│           ├── Sports
│           └── Squads
├── Core
│   ├── __pycache__
│   ├── __init__.py
│   ├── CsvScraper.py
│   ├── FixtureDetails.py
│   ├── LeaguesList.py
│   ├── MatchDetails.py
│   ├── PeriodData.py
│   ├── ScoreFlowData.py
│   └── Scraper.py
├── Data                                                        
├── DatabaseUtils
│   ├── PlayerTableCode
│       ├── CleanPlayerTable.py
│       ├── CreateStaticPlayerInfoTable.py
│       ├── ExportPlayerInfo.py
│       └── InsertStaticPlayerInfo.py
│   ├── columnChecker.py
│   ├── DatabaseHelper.py
│   ├── reconstructor.py
│   └── SqlConnector.py
├── Logs
│   ├── error.log
│   └── info.log
├── Utils
│   ├── CsvHelper.py
│   ├── JsonLoader.py
│   ├── Logger.py
│   ├── SanitiseFilename.py
│   └──SportCategory.py
├── README.md
├── Main.py
└── TestScraper.py
```




### Core Modules

#### Scraper.py
**Purpose**: The main script that orchestrates the entire scraping and data insertion process.

#### LeaguesList.py
**Purpose**: Fetches the list of available leagues from the Champion Data API.

#### FixtureDetails.py
**Purpose**: Fetches and processes fixture data for a specific league.

#### MatchDetails.py
**Purpose**: Fetches and processes match data for a specific match within a league.

#### PeriodData.py
**Purpose**: Fetches and processes period statistics data for a specific match.

#### ScoreFlowData.py
**Purpose**: Fetches and processes score flow data for a specific match.

#### SportCategory.py
**Purpose**: Determines the sport category based on input parameters like regulation periods, squad IDs, and league names.

#### DatabaseHelper.py
**Purpose**: Provides methods to interact with the MySQL database.

### Utils Modules

#### SqlConnector.py
**Purpose**: Manages the connection to the MySQL database.

#### Logger.py
**Purpose**: Sets up logging for the project.

#### JsonLoader.py
**Purpose**: Loads JSON configurations for the project.

#### SanitiseFilename.py
**Purpose**: Provides functions to sanitize filenames and directory names.

## Database Schema

### Tables and Fields
The database schema includes tables for:
- `sport_info`: Contains information about sports and fixtures.
- `squad_info`: Contains information about squads (teams).
- `player_info`: Contains information about players.
- Dynamic tables for fixtures, matches, periods, and score flows, named based on the sport category (e.g., `netball_womens_nz_fixture`).

### Relationships
- **One-to-Many**: A sport can have many fixtures.
- **One-to-Many**: A fixture can have many matches.
- **One-to-Many**: A match can have many period and score flow entries.
- **Many-to-One**: Players belong to squads, and squads participate in matches.

## Data Flow

### Fetching Leagues
The scraper fetches all available leagues using `LeaguesList.py`. Leagues are filtered and stored for processing.

### Processing Fixtures
Fixtures are fetched using `FixtureDetails.py`, and filtered to exclude incomplete or scheduled matches. Sport category and IDs are determined.

### Processing Matches
Match details are fetched using `MatchDetails.py`. Player stats are merged with player and team information.

### Processing Period Data
Period statistics are fetched using `PeriodData.py`. Data is merged with player information.

### Processing Score Flow Data
Score flow data is fetched using `ScoreFlowData.py`.

### Data Insertion
Processed data is inserted into the database using `DatabaseHelper.py`.

## Error Handling and Logging
Logging: Uses the logging module to record information and errors.
- **Info Logs**: General information about the scraping process.
- **Error Logs**: Detailed error messages and exceptions.

## Extending the Project

### Adding New Sports or Leagues
Update `SportCategory.py` to include new sports or adjust existing logic.
Add new create & insert queries, and update the file paths to reference these files.

## Known Issues and Considerations
- **API Changes**: The scraper depends on external APIs. Changes to the API may require updates.
- **Performance**: Processing large amounts of data may require optimization.
- **Bad Data**: Alot of the data is broken, some fallback methods work but generally you cannot fix this. 

## Conclusion
The Champion Data Scraper is a robust and flexible tool designed to collect and store detailed sports data.
