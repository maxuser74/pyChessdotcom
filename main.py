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

