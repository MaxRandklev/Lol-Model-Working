import tkinter as tk
from tkinter import scrolledtext, messagebox, Tk, Label, Button
import pandas as pd
from difflib import get_close_matches

def average_kills_against_teams(data, player_name, teams, results_text):
    player_name_lower = player_name.lower()
    teams_lower = [team.lower() for team in teams]
    player_data = data[data['playername'].str.lower() == player_name_lower]

    # Check if player data is found
    if player_data.empty:
        suggest_player_correction(data, player_name_lower, results_text)
        results_text.insert(tk.END, f"Player '{player_name}' not found in data.\n")
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
            results_text.insert(tk.END, f"Team '{team_lower}' not found in games for player '{player_name}'.\n")

    return results

def suggest_player_correction(data, player_name, results_text):
    # Convert all player names to strings and to lowercase
    all_players = data['playername'].astype(str).str.lower().unique()
    suggestions = get_close_matches(player_name, all_players, n=3, cutoff=0.6)
    if suggestions:
        suggestion_msg = f"No data found for '{player_name}'. Did you mean: {', '.join(suggestions)}?\n"
        results_text.insert(tk.END, suggestion_msg)

def suggest_team_correction(data, team, results_text):
    # Convert all team names to strings and to lowercase
    all_teams = data['teamname'].astype(str).str.lower().unique()

    # Ensure the input 'team' is also a string
    team_str = str(team).lower()

    suggestions = get_close_matches(team_str, all_teams, n=3, cutoff=0.6)
    if suggestions:
        suggestion_msg = f"No data found for '{team_str}'. Did you mean: {', '.join(suggestions)}?\n"
        results_text.insert(tk.END, suggestion_msg)

def read_and_concatenate_files(selected_files):
    dataframes=[pd.read_csv(filepath, low_memory=False) for filepath, var in selected_files.items() if var.get()]
    if not dataframes:
        messagebox.showerror('Error', 'Select at least one year.')
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)

root=tk.Tk()
root.title("LoL Average Kills Calculator")

file_paths={"2024":'2024_LoL_esports_match_data_from_OraclesElixir.csv',"2023":"2023_LoL_esports_match_data_from_OraclesElixir.csv","2022":'2022_LoL_esports_match_data_from_OraclesElixir.csv',"2021":'2021_LoL_esports_match_data_from_OraclesElixir.csv',"2020":'2020_LoL_esports_match_data_from_OraclesElixir.csv'}

file_selection={}
for file_name, file_path in file_paths.items():
    file_selection[file_path]=tk.BooleanVar(value=False)
    checkbox = tk.Checkbutton(root, text=file_name, variable=file_selection[file_path])
    checkbox.pack()

player_name_label=tk.Label(root,text="Player Name:")
player_name_label.pack()
player_name_entry=tk.Entry(root)
player_name_entry.pack()

team_name_label=tk.Label(root,text="Team Name:")
team_name_label.pack()
team_name_entry=tk.Entry()
team_name_entry.pack()

results_text = tk.Text(root, height=10, width=50, wrap=tk.WORD)
results_text.pack()


def calculate_and_show_results():
    player_name = player_name_entry.get()
    team_name = team_name_entry.get()
    teams = [team_name]

    concatenated_data = read_and_concatenate_files(file_selection)

    results_text.config(state=tk.NORMAL)  # Enable editing to insert text
    results_text.delete('1.0', tk.END)  # Clear previous results

    if concatenated_data.empty:
        results_text.insert(tk.END, "No data, ensure a year was selected.\n")
    else:
        average_kills_result = average_kills_against_teams(concatenated_data, player_name, teams, results_text)
        for team, (avg_kills, game_count) in average_kills_result.items():
            results_string = f"Average kills of player '{player_name}' against team '{team}': {avg_kills}, over {game_count} games.\n"
            results_text.insert(tk.END, results_string)

    if not average_kills_result:  # Check if the result is empty
        results_text.insert(tk.END, "No matching data found for the query.\n")

    results_text.config(state=tk.DISABLED)  # Disable editing after insertion

calculate_button=tk.Button(root,text="Calculate AVG Kills", command=calculate_and_show_results)
calculate_button.pack()

root.mainloop()