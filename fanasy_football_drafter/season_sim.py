import pandas as pd
import numpy as np
import random

class Player:
    def __init__(self, name, position, season_projection, injury_prob, std_dev):
        self.name = name
        self.position = position
        self.season_projection = season_projection
        self.injury_prob = injury_prob
        self.std_dev = std_dev
        self.weekly_points = []
        self.is_injured = False

    def simulate_week(self):
        """Simulates the player's performance for a week."""
        self.is_injured = random.random() < self.injury_prob  # Determine if injured this week
        if self.is_injured:
            self.weekly_points.append(0)
        else:
            weekly_points = max(0, np.random.normal(self.season_projection / 17, self.std_dev))
            self.weekly_points.append(weekly_points)

class Team:
    def __init__(self, players):
        self.players = players
        self.starting_lineup = []
        
    def set_starting_lineup(self):
        """Sets the starting lineup based on the health status and previous week's performance."""
        healthy_players = [p for p in self.players if not p.is_injured]
        
        # Group players by position
        position_groups = {}
        for player in healthy_players:
            position_groups.setdefault(player.position, []).append(player)

        # Select starters for each position
        self.starting_lineup = []
        if 'QB' in position_groups:
            self.starting_lineup.extend(sorted(position_groups['QB'], key=lambda x: x.weekly_points[-1] if x.weekly_points else 0, reverse=True)[:1])
        if 'RB' in position_groups:
            self.starting_lineup.extend(sorted(position_groups['RB'], key=lambda x: x.weekly_points[-1] if x.weekly_points else 0, reverse=True)[:2])
        if 'WR' in position_groups:
            self.starting_lineup.extend(sorted(position_groups['WR'], key=lambda x: x.weekly_points[-1] if x.weekly_points else 0, reverse=True)[:2])
        if 'TE' in position_groups:
            self.starting_lineup.extend(sorted(position_groups['TE'], key=lambda x: x.weekly_points[-1] if x.weekly_points else 0, reverse=True)[:1])
        if 'K' in position_groups:
            self.starting_lineup.extend(sorted(position_groups['K'], key=lambda x: x.weekly_points[-1] if x.weekly_points else 0, reverse=True)[:1])
        if 'DST' in position_groups:
            self.starting_lineup.extend(sorted(position_groups['DST'], key=lambda x: x.weekly_points[-1] if x.weekly_points else 0, reverse=True)[:1])

        # Select FLEX players (RB, WR, or TE)
        flex_candidates = [p for p in healthy_players if p.position in ['RB', 'WR', 'TE'] and p not in self.starting_lineup]
        self.starting_lineup.extend(sorted(flex_candidates, key=lambda x: x.weekly_points[-1] if x.weekly_points else 0, reverse=True)[:2])

    def simulate_season(self):
        """Simulates the entire season."""
        results = []
        for week in range(1, 18):
            print(f"Week {week}:")

            # Simulate each player's week
            for player in self.players:
                player.simulate_week()

            # Set the lineup for the week
            self.set_starting_lineup()
            
            # Calculate weekly total
            weekly_total = sum(player.weekly_points[-1] for player in self.starting_lineup)
            results.append((week, weekly_total))
            
            # Print weekly results
            print("  Starting lineup:")
            for player in self.starting_lineup:
                print(f"    {player.name} ({player.position}) - {player.weekly_points[-1]:.2f} points")
            print(f"  Weekly Total: {weekly_total:.2f}\n")

        return results

def load_players_from_csv(csv_path):
    """Loads player data from a CSV file."""
    df = pd.read_csv(csv_path)
    players = []
    for _, row in df.iterrows():
        player = Player(
            name=row['Name'],
            position=row['Position'],
            season_projection=row['SeasonProjection'],
            injury_prob=row['InjuryProb'],
            std_dev=row['StdDev']
        )
        players.append(player)
    return players

if __name__ == "__main__":
    # Load player data
    csv_path = "players.csv"  # Replace with your CSV file path
    players = load_players_from_csv(csv_path)

    # Create team and simulate season
    team = Team(players)
    season_results = team.simulate_season()

    # Print final results
    print("Final Season Results:")
    for week, total in season_results:
        print(f"  Week {week}: {total:.2f} points")
