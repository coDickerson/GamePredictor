import pandas as pd
import numpy as np
import soccerdata as sd

# Initialize data sources
fbref = sd.FBref()

# Top 5 European Leagues - 2024/25 Season
# 1. Premier League (England)
premier_league_fotmob = sd.FotMob(leagues="ENG-Premier League", seasons="2024/2025")
premier_league = premier_league_fotmob.read_league_table()
# 2. La Liga (Spain)
la_liga_fotmob = sd.FotMob(leagues="ESP-La Liga", seasons="2024/2025")
la_liga = la_liga_fotmob.read_league_table()
# 3. Bundesliga (Germany)
bundesliga_fotmob = sd.FotMob(leagues="GER-Bundesliga", seasons="2024/2025")
bundesliga = bundesliga_fotmob.read_league_table()
# 4. Serie A (Italy)
serie_a_fotmob = sd.FotMob(leagues="ITA-Serie A", seasons="2024/2025")
serie_a = serie_a_fotmob.read_league_table()
# 5. Ligue 1 (France)
ligue_1_fotmob = sd.FotMob(leagues="FRA-Ligue 1", seasons="2024/2025")
ligue_1 = ligue_1_fotmob.read_league_table()

league_input = input("Enter league table: ").lower()

# Dictionary mapping input variations to dataframes
league_tables = {
    'england': premier_league,
    'premier league': premier_league,
    'epl': premier_league,
    'spain': la_liga, 
    'la liga': la_liga,
    'germany': bundesliga,
    'bundesliga': bundesliga,
    'italy': serie_a,
    'serie a': serie_a,
    'france': ligue_1,
    'ligue 1': ligue_1
}

if league_input in league_tables:
    print("\nShowing table for", league_input.title())
    print(league_tables[league_input])
else:
    print("League not found. Available options: England/Premier League, Spain/La Liga, Germany/Bundesliga, Italy/Serie A, France/Ligue 1")
