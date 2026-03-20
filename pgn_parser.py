# Purpose of this file: implement functions to unzip & parse pgn datasets
#   --> obtain a new dataset with manually-selected variables

import sys
import zipfile
from zipfile import ZipFile
import csv
from pathlib import Path
import chess, chess.pgn
import numpy as np
import numpy.typing as npt

def extract_pgns(data_dir):
    path_name = Path(data_dir)
    for i, file_name in enumerate(path_name.iterdir()):
        file_str = str(file_name)
        print(file_str)
        if (zipfile.is_zipfile(file_str)):
            with ZipFile(file_str, 'r') as zObject:
                zObject.extract(file_str[file_str.index('/')+1:file_str.index('g.')] + ".pgn", \
                          path= data_dir)
            zObject.close()
    
### variable list:
###     [moves near king, moves past half rank, amt pawns past half rank, 
###      amt pieces left on board by eog, amt pawns left on board by eog,
###      length of game, ]
if __name__ == "__main__":
    extract_pgns("./twic_datasets")

    player_stats: dict[npt.NDArray[np.int64]] = {}
    path_name = Path("./twic_datasets")
    for pgn_idx in range(int(sys.argv[1]), int(sys.argv[2])):
        pgn = open("./twic_datasets/twic16" + str(pgn_idx) + ".pgn")
        game = chess.pgn.read_game(pgn)
        game_idx = 0
        while ((game != None) and (game_idx < 15)):
            board = game.board()
            wking_pos, bking_pos = None, None
            wplayer = game.headers["White"]
            bplayer = game.headers["Black"]
            if (wplayer not in player_stats.keys()):
                player_stats[wplayer] = np.zeros(0, 6)
            if (bplayer not in player_stats.keys()):
                player_stats[bplayer] = np.zeros(0, 6)

            player_stats[wplayer][5] = len(list(game.mainline_moves()))//2
            player_stats[bplayer][5] = len(list(game.mainline_moves()))//2
            for move in game.mainline_moves():
                curr_piece = board.piece_at(move.from_square)
                curr_color = board.color_at(move.from_square)

                # move -> variable checking
            game = chess.pgn.read_game(pgn)
            game_idx += 1
            
    with open("player_data_30-36.csv", 'w', newline='') as csvfile:
        player_writer = csv.writer(csvfile, delimiter=', ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for player in player_stats.keys():
            player_writer.writerow([player] + player_stats[player].tolist())

