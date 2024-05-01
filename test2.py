from chessdotcom import (
                         Client,
                         get_player_games_by_month_pgn)

import re
import pandas as pd

Client.request_config["headers"]["User-Agent"] = (
   "My Python Application. "
   "Contact me at email@example.com"
)

games_data = str(get_player_games_by_month_pgn('macspacs', '2024', '04').json['pgn']['pgn'])

def format_time(seconds):
    """Helper function to convert seconds into MM:SS format."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


def parse_pgn_data(pgn_text):
    metadata_pattern = re.compile(r"\[(\w+)\s+\"(.*?)\"\]")
    game_sections = re.split(r"(?=\[Event)", pgn_text)[1:]  # Split and remove empty first element

    games_data = []

    for game in game_sections:
        game_data = {}

        metadata = dict(metadata_pattern.findall(game))
        # Convert date_time to a datetime object for proper sorting
        game_data['date_time'] = pd.to_datetime(f"{metadata['UTCDate']} {metadata['UTCTime']}")
        game_data['macspacs_elo'] = int(metadata['WhiteElo'] if metadata['White'] == 'macspacs' else metadata['BlackElo'])
        game_data['opponent_elo'] = int(metadata['BlackElo'] if metadata['White'] == 'macspacs' else metadata['WhiteElo'])
        
        if metadata['White'] == 'macspacs':
            game_data['macspacs_color'] = 'White'
            game_data['final_result'] = 'win' if metadata['Result'] == '1-0' else 'loss' if metadata['Result'] == '0-1' else 'draw'
        else:
            game_data['macspacs_color'] = 'Black'
            game_data['final_result'] = 'win' if metadata['Result'] == '0-1' else 'loss' if metadata['Result'] == '1-0' else 'draw'

        moves_clocks_pattern = re.compile(r"{\[.*?clk (\d+):(\d\d):(\d\d)(?:\.\d)?\]}")
        moves = moves_clocks_pattern.findall(game)

        times = [int(h) * 3600 + int(m) * 60 + int(s) for h, m, s in moves]
        if metadata['White'] == 'macspacs':
            macspacs_times = times[0::2]
            opponent_times = times[1::2]
        else:
            macspacs_times = times[1::2]
            opponent_times = times[0::2]

        game_data['remaining_time_macspacs'] = format_time(macspacs_times[-1])
        game_data['remaining_time_opponent'] = format_time(opponent_times[-1])
        
        # Count of moves needs to be half the length of the total moves recorded (white + black)
        game_data['total_moves'] = (len(times) + 1) // 2  # +1 to handle any final single move

        if len(macspacs_times) > 12:
            opening_times = [macspacs_times[i] - macspacs_times[i+1] for i in range(11)]
            middle_end_times = [macspacs_times[i] - macspacs_times[i+1] for i in range(11, len(macspacs_times)-1)]
            game_data['avg_move_time_opening_macspacs'] = sum(opening_times) / len(opening_times) if opening_times else None
            game_data['avg_move_time_middle_end_game_macspacs'] = sum(middle_end_times) / len(middle_end_times) if middle_end_times else None
        else:
            opening_times = [macspacs_times[i] - macspacs_times[i+1] for i in range(len(macspacs_times)-1)]
            game_data['avg_move_time_opening_macspacs'] = sum(opening_times) / len(opening_times) if opening_times else None
            game_data['avg_move_time_middle_end_game_macspacs'] = None

        game_data['termination'] = metadata['Termination']

        games_data.append(game_data)

    df_columns = ['date_time', 'macspacs_elo', 'opponent_elo', 'final_result',
                  'remaining_time_macspacs', 'remaining_time_opponent', 'total_moves',
                  'avg_move_time_opening_macspacs', 'avg_move_time_middle_end_game_macspacs',
                  'macspacs_color', 'termination']
    games_df = pd.DataFrame(games_data, columns=df_columns)

    # Sort the DataFrame by 'date_time'
    games_df = games_df.sort_values(by='date_time', ascending=True)
    return games_df

df = parse_pgn_data(games_data)

# Convert DataFrame to string
text_representation = df.to_string(index=False)
# Write string to file
with open('datas_df.txt', 'w') as file:
    file.write(text_representation)