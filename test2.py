from chessdotcom import (
                         Client,
                         get_player_games_by_month_pgn)

from datetime import datetime, timedelta
import re
import pandas as pd
import chess
import io


Client.request_config["headers"]["User-Agent"] = (
   "My Python Application. "
   "Contact me at email@example.com"
)

games_data_str = str(get_player_games_by_month_pgn('macspacs', '2024', '05').json['pgn']['pgn'])

def split_pgn_games(content):
    
    games = []
    game_content = []
    lines = content.split('\n')
    
    for line in lines:
        if line.startswith('[Event') and game_content:
            # When a new game starts, join the previous game's content and add to the list
            games.append('\n'.join(game_content))
            game_content = []  # Reset for the next game
        
        game_content.append(line)  # Add the current line to the game content
    
    # Add the last game if the file doesn't end with a new [Event immediately after the last game
    if game_content:
        games.append('\n'.join(game_content))
    
    return games

game0 = split_pgn_games(games_data_str)[0]


#df = parse_pgn('macspacs',games_data_str)

# Convert DataFrame to string
#text_representation = df.to_string(index=False)
# Write string to file
#with open('datas_df.txt', 'w') as file:
#    file.write(games_data_str)

