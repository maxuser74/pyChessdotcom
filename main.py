from chessdotcom import (get_player_profile,
                         Client, get_player_stats,
                         get_player_games_by_month_pgn,
                         get_player_games_by_month)

import chess.pgn
import io
import re
import pandas as pd

game_headers = ['Event', 'Site', 'Date', 'Round', 'White',
                'Black', 'Result', 'CurrentPosition', 'Timezone',
                'ECO', 'ECOUrl', 'UTCDate', 'UTCTime', 'WhiteElo',
                'BlackElo', 'TimeControl', 'Termination', 'StartTime',
                'EndDate', 'EndTime', 'Link']

Client.request_config["headers"]["User-Agent"] = (
   "My Python Application. "
   "Contact me at email@example.com"
)
response = get_player_profile("macspacs")

response2 = get_player_stats("macspacs")
#print(json.dumps(response2.json['stats'], indent=3))
print('Rapid last: ', response2.json['stats']['chess_rapid']['last']['rating'])
print('Rapid best: ', response2.json['stats']['chess_rapid']['best']['rating'])

# get all games for a specific month
games = get_player_games_by_month('macspacs', '2024', '04').json['games']
row = []
for i in range(0, (len(games) - 1)):
    pgn = io.StringIO(games[i]['pgn'])
    curr_game = chess.pgn.read_game(pgn)
    for y in game_headers:
        try:
            row.append(curr_game.headers[y])
        except:
            row.append("ND")


game = games[0]['pgn']
#print(game)

#f = open("test.pgn", "w")
#f.write(game)
#f.close()

def extract_pgn_text(text):
    lines = text.split('\n')
    
    # Find the index of the line that contains "[Link"
    link_index = -1
    for i, line in enumerate(lines):
        if "[Link" in line:
            link_index = i
            break
    
    if link_index == -1:
        return "No [Link found in text."
    
    # Remove all lines up to and including the line with "[Link"
    # Also check for the subsequent empty line and remove it if present
    post_link_lines = lines[link_index + 1:]
    if post_link_lines and post_link_lines[0].strip() == '':
        post_link_lines = post_link_lines[1:]
    
    # Rejoin the remaining text
    remaining_text = '\n'.join(post_link_lines)
    
    # Find the position of the substring "1." in the remaining text
    one_index = remaining_text.find("1.")
    if one_index == -1:
        return "Substring '1.' not found in the text after [Link."
    
    # Return the text starting from "1."
    return remaining_text[one_index:]

def extract_move_times(pgn, gameplay_start_time):

       # Helper function to convert time string to total seconds
    def time_to_seconds(t):
        h, m, s = map(float, t.split(':'))
        return h * 3600 + m * 60 + s

    # Helper function to format seconds back to h:mm:ss.s
    def seconds_to_hmmss(s):
        hours = int(s // 3600)
        minutes = int((s % 3600) // 60)
        seconds = s % 60
        return f"{hours}:{minutes:02}:{seconds:.1f}"

    # Correct regex pattern to capture the move number, dot notation, move, and clock time
    move_pattern = re.compile(r'(\d+)(\.|\.{3})\s*([^\s]+)\s*\{\[%clk\s+([^\]]+)\]\}')
    
    # Dictionaries to store times for white and black moves indexed by move number
    white_times = {}
    black_times = {}
    
    # Iterate over all matches in the PGN string
    for match in move_pattern.finditer(pgn):
        move_number = int(match.group(1))  # Move number
        dots = match.group(2)              # Dots to differentiate white or black move
        time_str = match.group(4)          # Time string like "0:09:59.9"
        seconds = time_to_seconds(time_str)  # Convert time string to seconds
        
        if dots == ".":  # White's move
            white_times[move_number] = seconds
        elif dots == "...":  # Black's move
            black_times[move_number] = seconds
    
    # Convert dictionaries to Series with move number as index
    white_series = pd.Series(white_times, name="White times")
    black_series = pd.Series(black_times, name="Black times")

    # Create a DataFrame from the collected times
    df = pd.DataFrame({
        "White times": white_series,
        "Black times": black_series
    })

    # Calculate time differences
    initial_white_seconds = time_to_seconds(gameplay_start_time)
    initial_black_seconds = time_to_seconds(gameplay_start_time)

    df['White diff'] = df['White times'].diff().fillna(df['White times'].iloc[0] - initial_white_seconds)
    df['Black diff'] = df['Black times'].diff().fillna(df['Black times'].iloc[0] - initial_black_seconds)

    # Format the times and differences for display
    df['White times'] = df['White times'].apply(seconds_to_hmmss)
    df['Black times'] = df['Black times'].apply(seconds_to_hmmss)
    df['White diff'] = df['White diff'].map(lambda x: f"{x:.1f}")
    df['Black diff'] = df['Black diff'].map(lambda x: f"{x:.1f}")

    return df

pgn_text = extract_pgn_text(game)
print(pgn_text)

print(extract_move_times(pgn_text,'0:10:00'))

