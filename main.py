from chessdotcom import (get_player_profile,
                         Client, get_player_stats,
                         get_player_games_by_month_pgn,
                         get_player_games_by_month)

import chess.pgn
import io

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
print(game)

#f = open("test.pgn", "w")
#f.write(game)
#f.close()

def extract_post_link_text(text):
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

print(extract_post_link_text(game))

      