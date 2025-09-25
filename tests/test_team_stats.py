#!/usr/bin/env python3
"""
Quick test of the team statistics aggregator
"""

from team_stats_aggregator import TeamStatsAggregator

def test_team_stats():
    """Test the team statistics aggregator with a specific team"""
    
    aggregator = TeamStatsAggregator()
    
    # Test with Arsenal in Premier League (we know this team exists)
    print("Testing with Arsenal in Premier League...")
    try:
        stats_df = aggregator.display_team_stats("england", "Arsenal")
        if stats_df is not None:
            print("\n✅ Test completed successfully!")
            return stats_df
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        
        # Try to show available teams to help debug
        print("\nTrying to show available teams for debugging...")
        try:
            teams = aggregator.get_available_teams("england")
            print(f"Available teams in England: {teams}")
        except Exception as debug_e:
            print(f"Debug error: {debug_e}")
        
        return None

if __name__ == "__main__":
    test_team_stats()
