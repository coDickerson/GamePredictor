import pandas as pd
import numpy as np
import soccerdata as sd
from typing import Dict, List, Optional
import time

class AdvancedTeamStatsAggregator:
    """
    Advanced team statistics aggregator with real FBref data integration.
    """
    
    def __init__(self):
        self.fotmob = sd.FotMob()
        self.fbref = sd.FBref()
        
        # League mappings
        self.league_mappings = {
            'england': 'ENG-Premier League',
            'premier league': 'ENG-Premier League', 
            'epl': 'ENG-Premier League',
            'spain': 'ESP-La Liga',
            'la liga': 'ESP-La Liga',
            'germany': 'GER-Bundesliga',
            'bundesliga': 'GER-Bundesliga',
            'italy': 'ITA-Serie A',
            'serie a': 'ITA-Serie A',
            'france': 'FRA-Ligue 1',
            'ligue 1': 'FRA-Ligue 1'
        }
        
        # FBref league mappings (different format)
        self.fbref_league_mappings = {
            'england': 'Premier League',
            'premier league': 'Premier League',
            'epl': 'Premier League',
            'spain': 'La Liga',
            'la liga': 'La Liga',
            'germany': 'Bundesliga',
            'bundesliga': 'Bundesliga',
            'italy': 'Serie A',
            'serie a': 'Serie A',
            'france': 'Ligue 1',
            'ligue 1': 'Ligue 1'
        }
        
        self.seasons = ['2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021']
    
    def get_fbref_team_stats(self, league: str, team: str) -> Optional[pd.DataFrame]:
        """
        Get advanced team statistics from FBref.
        Note: This may take time due to data download.
        """
        try:
            print(f"Fetching advanced statistics from FBref for {team}...")
            
            # Get standard team stats
            standard_stats = self.fbref.read_team_season_stats(stat_type='standard')
            
            # Get possession stats
            possession_stats = self.fbref.read_team_season_stats(stat_type='possession')
            
            # Get shooting stats
            shooting_stats = self.fbref.read_team_season_stats(stat_type='shooting')
            
            # Filter for the specific team and league
            league_name = self.fbref_league_mappings.get(league.lower())
            if not league_name:
                return None
            
            # Combine the data
            team_data = []
            for season in self.seasons:
                season_data = {}
                
                # Standard stats
                std_data = standard_stats[
                    (standard_stats['league'] == league_name) & 
                    (standard_stats['season'] == season) &
                    (standard_stats['team'].str.contains(team, case=False, na=False))
                ]
                
                if not std_data.empty:
                    std_row = std_data.iloc[0]
                    season_data.update({
                        'Season': season,
                        'Team': std_row['team'],
                        'League': league_name,
                        'Matches_Played': std_row.get('mp', 0),
                        'Wins': std_row.get('w', 0),
                        'Draws': std_row.get('d', 0),
                        'Losses': std_row.get('l', 0),
                        'Goals_For': std_row.get('gf', 0),
                        'Goals_Against': std_row.get('ga', 0),
                        'Goal_Difference': std_row.get('gd', 0),
                        'Points': std_row.get('pts', 0)
                    })
                
                # Possession stats
                poss_data = possession_stats[
                    (possession_stats['league'] == league_name) & 
                    (possession_stats['season'] == season) &
                    (possession_stats['team'].str.contains(team, case=False, na=False))
                ]
                
                if not poss_data.empty:
                    poss_row = poss_data.iloc[0]
                    season_data['Avg_Possession'] = poss_row.get('poss', 0)
                
                # Shooting stats
                shot_data = shooting_stats[
                    (shooting_stats['league'] == league_name) & 
                    (shooting_stats['season'] == season) &
                    (shooting_stats['team'].str.contains(team, case=False, na=False))
                ]
                
                if not shot_data.empty:
                    shot_row = shot_data.iloc[0]
                    season_data['Shots_Per_Game'] = shot_row.get('sh', 0) / season_data.get('Matches_Played', 1)
                    season_data['Shots_on_Target_Per_Game'] = shot_row.get('sot', 0) / season_data.get('Matches_Played', 1)
                
                if season_data:
                    team_data.append(season_data)
            
            return pd.DataFrame(team_data) if team_data else None
            
        except Exception as e:
            print(f"Error fetching FBref data: {str(e)}")
            return None
    
    def get_hybrid_team_stats(self, league: str, team: str) -> pd.DataFrame:
        """
        Get team statistics combining FotMob (fast) and FBref (detailed) data.
        """
        print(f"Getting hybrid statistics for {team} in {league}...")
        
        # First, try to get basic stats from FotMob (fast)
        try:
            from team_stats_aggregator import TeamStatsAggregator
            basic_aggregator = TeamStatsAggregator()
            basic_stats = basic_aggregator.get_team_league_table_stats(league, team)
            print("✅ Basic statistics retrieved from FotMob")
        except Exception as e:
            print(f"❌ Error getting basic stats: {str(e)}")
            return None
        
        # Try to enhance with FBref data (slower but more detailed)
        print("Attempting to enhance with FBref data...")
        fbref_stats = self.get_fbref_team_stats(league, team)
        
        if fbref_stats is not None and not fbref_stats.empty:
            print("✅ Advanced statistics retrieved from FBref")
            # Merge the data
            merged_stats = pd.merge(
                basic_stats, 
                fbref_stats[['Season', 'Avg_Possession', 'Shots_Per_Game', 'Shots_on_Target_Per_Game']], 
                on='Season', 
                how='left'
            )
            
            # Fill missing values with estimates
            merged_stats['Avg_Possession'] = merged_stats['Avg_Possession'].fillna(
                merged_stats.apply(lambda row: min(65, max(35, 50 + (row['Goal_Difference'] * 0.3))), axis=1)
            )
            merged_stats['Shots_Per_Game'] = merged_stats['Shots_Per_Game'].fillna(
                merged_stats['Goals_Per_Game'] * 6
            )
            merged_stats['Shots_on_Target_Per_Game'] = merged_stats['Shots_on_Target_Per_Game'].fillna(
                merged_stats['Shots_Per_Game'] * 0.35
            )
            
            return merged_stats
        else:
            print("⚠️  Using estimated advanced statistics")
            # Fall back to basic stats with estimates
            return basic_stats

def main():
    """
    Test the advanced team statistics aggregator.
    """
    aggregator = AdvancedTeamStatsAggregator()
    
    print("🚀 ADVANCED TEAM STATISTICS AGGREGATOR")
    print("=" * 60)
    print("This version attempts to get real advanced statistics from FBref")
    print("(Note: This may take longer due to data download)")
    print()
    
    league = input("Enter league (e.g., 'england'): ").strip()
    team = input("Enter team name (e.g., 'Arsenal'): ").strip()
    
    if league and team:
        try:
            stats_df = aggregator.get_hybrid_team_stats(league, team)
            
            if stats_df is not None:
                print(f"\n{'='*80}")
                print(f"ADVANCED STATISTICS: {team.upper()} - {league.upper()}")
                print(f"{'='*80}")
                print(stats_df.to_string(index=False))
                
                # Summary
                print(f"\n{'='*50}")
                print("SUMMARY")
                print(f"{'='*50}")
                print(f"Average Points: {stats_df['Points'].mean():.1f}")
                print(f"Average Goals per Game: {stats_df['Goals_Per_Game'].mean():.2f}")
                if 'Avg_Possession' in stats_df.columns:
                    print(f"Average Possession: {stats_df['Avg_Possession'].mean():.1f}%")
                if 'Shots_Per_Game' in stats_df.columns:
                    print(f"Average Shots per Game: {stats_df['Shots_Per_Game'].mean():.1f}")
            else:
                print("❌ Could not retrieve team statistics")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
