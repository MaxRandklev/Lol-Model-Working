import pandas as pd
from difflib import get_close_matches
from flask import Flask, request, render_template

app=Flask(__name__)

def average_kills_against_teams(data, player_name, teams, results_text):
    player_name_lower = player_name.lower()
    teams_lower = [team.lower() for team in teams]
    player_data = data[data['playername'].str.lower() == player_name_lower]

    # Check if player data is found
    if player_data.empty:
        suggest_player_correction(data, player_name_lower, results_text)
        return {}

    results = {}
    for team_lower in teams_lower:
        team_found = False
        total_kills = 0
        game_count = 0

        for game_id in player_data['gameid'].unique():
            game_data = data[data['gameid'] == game_id]
            teams_in_game = game_data['teamname'].str.lower().unique()

            if team_lower in teams_in_game and len(teams_in_game) == 2:
                team_found = True
                player_game_data = game_data[game_data['playername'].str.lower() == player_name_lower]
                total_kills += player_game_data['kills'].sum()
                game_count += 1

        avg_kills = total_kills / game_count if game_count > 0 else 0
        results[team_lower] = (avg_kills, game_count)
        if not team_found:
            suggest_team_correction(data, team_lower, results_text)

    return results

def suggest_player_correction(data, player_name, results_text):
    # Convert all player names to strings and to lowercase
    all_players = data['playername'].astype(str).str.lower().unique()
    suggestions = get_close_matches(player_name, all_players, n=3, cutoff=0.6)
    if suggestions:
        suggestion_msg = f"No data found for '{player_name}'. Did you mean: {', '.join(suggestions)}?\n"

def suggest_team_correction(data, team, results_text):
    # Convert all team names to strings and to lowercase
    all_teams = data['teamname'].astype(str).str.lower().unique()

    # Ensure the input 'team' is also a string
    team_str = str(team).lower()

    suggestions = get_close_matches(team_str, all_teams, n=3, cutoff=0.6)
    if suggestions:
        suggestion_msg = f"No data found for '{team_str}'. Did you mean: {', '.join(suggestions)}?\n"

def read_and_concatenate_files(selected_files):
    dataframes=[pd.read_csv(filepath, low_memory=False) for filepath, var in selected_files.items() if var.get()]
    if not dataframes:
        messagebox.showerror('Error', 'Select at least one year.')
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)
