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
#print(games)

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
#print(pgn_text)

result_df = extract_move_times(pgn_text,'0:10:00')

def calculate_average_times(df):
    import pandas as pd

    # Convert differences back to float for calculations
    df['White diff'] = df['White diff'].astype(float)
    df['Black diff'] = df['Black diff'].astype(float)
    
    # Define opening and middlegame based on move numbers
    opening_end = 12
    middlegame_start = 13
    
    # Calculate average times for opening (first 12 moves)
    if len(df) >= opening_end:
        opening_avg_white = df.loc[1:opening_end, 'White diff'].mean()
        opening_avg_black = df.loc[1:opening_end, 'Black diff'].mean()
    else:
        opening_avg_white = df['White diff'].mean()  # If less than 12 moves in total
        opening_avg_black = df['Black diff'].mean()

    # Calculate average times for middlegame (from move 13 to end)
    if len(df) >= middlegame_start:
        middlegame_avg_white = df.loc[middlegame_start:, 'White diff'].mean()
        middlegame_avg_black = df.loc[middlegame_start:, 'Black diff'].mean()
    else:
        middlegame_avg_white = None  # No middlegame moves if less than 13 moves
        middlegame_avg_black = None

    # Return a DataFrame with the results
    avg_times_df = pd.DataFrame({
        'Phase': ['Opening', 'Middlegame'],
        'Average White Time (s)': [opening_avg_white, middlegame_avg_white],
        'Average Black Time (s)': [opening_avg_black, middlegame_avg_black]
    })

    return avg_times_df

def create_games_dataframe(pgn_texts):
    # Define a list to store game data
    games_data = []

    # Define the regex patterns for extracting data from PGN text
    game_info_pattern = re.compile(r"""
        \[Date\s+"(?P<Date>\d{4}\.\d{2}\.\d{2})"\]
        .*\[White\s+"(?P<White>[^"]+)"\]
        .*\[Black\s+"(?P<Black>[^"]+)"\]
        .*\[Result\s+"(?P<Result>[^"]+)"\]
        .*\[UTCDate\s+"(?P<UTCDate>\d{4}\.\d{2}\.\d{2})"\]
        .*\[UTCTime\s+"(?P<UTCTime>\d{2}:\d{2}:\d{2})"\]
        .*\[WhiteElo\s+"(?P<WhiteElo>\d+)"\]
        .*\[BlackElo\s+"(?P<BlackElo>\d+)"\]
        .*\[TimeControl\s+"(?P<TimeControl>\d+)"\]
        .*\[Termination\s+"(?P<Termination>[^"]+)"\]
        """, re.DOTALL | re.VERBOSE)

    # Loop through each PGN text to extract game information
    for pgn in pgn_texts:
        match = game_info_pattern.search(pgn)
        if match:
            game_info = match.groupdict()
            game_info['TimeControl'] = int(game_info['TimeControl'])  # Convert to int
            game_info['WhiteElo'] = int(game_info['WhiteElo'])  # Convert to int
            game_info['BlackElo'] = int(game_info['BlackElo'])  # Convert to int
            game_info['Winner'] = 'Draw' if game_info['Result'] == '1/2-1/2' else (
                game_info['White'] if game_info['Result'] == '1-0' else game_info['Black'])
            games_data.append(game_info)

    # Create a DataFrame from the collected game information
    df = pd.DataFrame(games_data)
    return df

#print(calculate_average_times(result_df))

test = get_player_games_by_month_pgn('macspacs', '2024', '04')

test2 = str(test.json['pgn']['pgn'])

print(create_games_dataframe(test2))


