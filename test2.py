from chessdotcom import (
                         Client,
                         get_player_games_by_month_pgn)

from datetime import datetime, timedelta
import re
import pandas as pd

Client.request_config["headers"]["User-Agent"] = (
   "My Python Application. "
   "Contact me at email@example.com"
)

games_data_str = str(get_player_games_by_month_pgn('macspacs', '2024', '05').json['pgn']['pgn'])

def pgn_to_df(specified_player, pgn_txt):
    # Split the PGN text into individual games
    games = pgn_txt.strip().split("\n\n")
    
    # Prepare a list to hold game data
    data = []

    # Regex to extract relevant data from PGN headers
    pattern = re.compile(r"\[(\w+) \"(.*?)\"\]")

    for game in games:
        game_info = dict(pattern.findall(game))
        print(game_info)

        player_elo = 0
        opponent_elo = 0 
        elo_difference = 0

        # Determine player color and relevant Elo ratings
        if specified_player == game_info.get("White"):
            player_color = "White"
            player_elo = int(game_info.get("WhiteElo"))
            opponent_elo = int(game_info.get("BlackElo"))
            print(player_color)
            print(player_elo)
            print(opponent_elo)
            print(player_elo - opponent_elo)
        else:
            player_color = "Black"
            player_elo = int(game_info.get("BlackElo"))
            opponent_elo = int(game_info.get("WhiteElo"))
            print(player_color)
            print(player_elo)
            print(opponent_elo)
            print(player_elo - opponent_elo)        


        # Calculate Elo difference
        print(player_elo)
        print(opponent_elo)
        
        elo_difference = player_elo - opponent_elo
        
        # Time control conversion
        seconds = int(game_info.get("TimeControl"))
        time_control_formatted = str(timedelta(seconds=seconds))
        
        # Extract remaining time for the specified player from the move text
        # We assume the last occurrence of [%clk time] gives the remaining time.
        try:
            remaining_time = re.findall(r"\[%clk (\d+:\d+:\d+(?:\.\d+)?)\]", game)[-1]
        except IndexError:
            remaining_time = None
        
        # Extract the game result for the specified player
        if game_info["Result"] == "1-0":
            result = "won" if player_color == "White" else "lost"
        elif game_info["Result"] == "0-1":
            result = "won" if player_color == "Black" else "lost"
        else:
            result = "drew"

        # Extract opening from the ECOUrl
        opening = game_info.get("ECOUrl").split("/")[-1]

        # Count number of full moves (assuming one move per line starting with move number)
        moves_count = len(re.findall(r"\d+\.", game))

        # Create a dictionary for the current game
        game_data = {
            "datetime": game_info.get("UTCDate") + " " + game_info.get("UTCTime"),
            "game_type": time_control_formatted,
            "specified_player_elo": player_elo,
            "specified_player_color": player_color,
            "opponent_elo": opponent_elo,
            "elo_difference": elo_difference,
            "final_result": game_info.get("Result"),
            "remaining_time": remaining_time,
            "termination": game_info.get("Termination"),
            "result": result,
            "opening": opening,
            "moves_played": moves_count
        }

        # Append to the data list
        data.append(game_data)
    
    # Create DataFrame
    df = pd.DataFrame(data)

    # Convert datetime to proper datetime format and sort
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.sort_values(by='datetime', inplace=True)

    return df


df = pgn_to_df('macspacs', games_data_str)

# Convert DataFrame to string
text_representation = df.to_string(index=False)
# Write string to file
with open('datas_df.txt', 'w') as file:
    file.write(games_data_str)

