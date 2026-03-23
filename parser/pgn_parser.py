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
from enum import IntEnum

### variable list (all averages):
###     [#GAMES, moves near king, moves toward king, moves past half rank, amt pawns past half rank, 
###      amt pieces left on board by eog, amt pawns left on board by eog, # king moves
###      length of game]
### Eventually: enum type for all the different variables
class Vars_idx(IntEnum):
    NUM_GAME = 0
    LEN_GAME = 1
    NEAR_KING = 2
    TO_KING = 3
    PIECE_PASTHF = 4
    PAWN_PASTHF = 5
    NUMPIECE_EOG = 6
    NUMPAWN_EOG = 7
    KING_MOVE = 8
NUM_VARS: int = len(Vars_idx)

def extract_pgns(data_dir):
    """
    Extracts all PGNs from the .zip files within data_dir
    """
    path_name = Path(data_dir)
    for file_name in path_name.iterdir():
        file_str = str(file_name)
        print(file_str)
        if (zipfile.is_zipfile(file_str)):
            with ZipFile(file_str, 'r') as zObject:
                zObject.extract(file_str[file_str.index('/')+1:file_str.index('g.')] + ".pgn", \
                          path= data_dir)
            zObject.close()

def create_squares_vector(init_square: chess.Square, final_square: chess.Square):
    """
    Creates a 2D vector from the initial square to the final square
    Returns (npt.NDArray[int]): resulting vector between input squares
    """
    vec_x, vec_y = 0, 0
    if (type(init_square) == chess.Square and type(final_square) == chess.Square):
        vec_x = final_square.square_file - init_square.square_file
        vec_y = final_square.square_rank - init_square.square_rank
    else:
        raise TypeError("Inputs are not valid chess.Square types")
    
    return np.array([vec_x, vec_y])

def get_color_player(wplayer: str, bplayer: str, color: chess.Color):
    """
    Gets the player name of the given player color
    Returns (str): name of the player associated with color
    """
    if (type(color) != chess.Color):
        raise TypeError("Input color is not a valid chess.Color type")
    if (color == chess.WHITE):
        return wplayer
    return bplayer

def get_move_data(move: chess.Move):
    """
    Gets all variables for move data from a given move (Prototype 1)
    Returns (npt.NDArray[int], chess.Square): data vector for the given move + new opponent king position
    """
    curr_piece = board.piece_at(move.from_square)
    curr_color = board.color_at(move.from_square)

    # move -> variable checking

    # directional checks (e.g. moves towards king):
    move_vec = create_squares_vector(move.from_square, move.to_square)
    king_vec = None
    new_king_square = -1
    if (curr_color == chess.WHITE):
        king_vec = create_squares_vector(move.from_square, bking_square)
    else:
        king_vec = create_squares_vector(move.from_square, wking_square)

    if (king_vec[0] * move_vec[0] > 0):
        player_stats[get_color_player(wplayer, bplayer, curr_color)][1] += 1

    # king position update:
    if (curr_piece.piece_type == chess.KING):
        if (curr_piece.color == chess.WHITE):
            new_king_square = move.from_square
        else:
            new_king_square = move.from_square    
    
    return move_stats, new_king_square

def get_move_data(move: chess.Move):
    """
    Gets all variables for move data from a given move
    Returns (npt.NDArray[int]): data vector for the given move
    """
    return np.zeros(NUM_VARS), -1

if __name__ == "__main__":
    extract_pgns("./twic_datasets")

    player_stats: dict[npt.NDArray[np.int64]] = {}
    path_name = Path("./twic_datasets")
    for pgn_idx in range(int(sys.argv[1]), int(sys.argv[2])+1):
        print("curr pgn twic: ./twic_datasets/twic16" + str(pgn_idx) + ".pgn")
        pgn = open("./twic_datasets/twic16" + str(pgn_idx) + ".pgn")
        game = chess.pgn.read_game(pgn)
        game_idx = 0
        while ((game != None) and (game_idx < 100)):
            print(f"curr game idx: {game_idx}")
            board = game.board()
            wking_square, bking_square = chess.E1, chess.E8
            wplayer = game.headers["White"]
            bplayer = game.headers["Black"]
            if (',' not in wplayer and ' ' in wplayer):
                wplayer = wplayer[:wplayer.index(' ')] + ',' + wplayer[wplayer.index(' ')+1:]
            if (',' not in bplayer and ' ' in bplayer):
                bplayer = bplayer[:bplayer.index(' ')] + ',' + bplayer[bplayer.index(' ')+1:]
            
            if (wplayer not in player_stats.keys()):
                player_stats[get_color_player(wplayer, bplayer, chess.WHITE)] = np.zeros(NUM_VARS)
                player_stats[get_color_player(wplayer, bplayer, chess.WHITE)] = np.zeros(NUM_VARS)
            if (bplayer not in player_stats.keys()):
                player_stats[get_color_player(wplayer, bplayer, chess.BLACK)] = np.zeros(NUM_VARS)
            
            player_stats[wplayer][Vars_idx.NUM_GAME+1:] *= player_stats[wplayer][Vars_idx.NUM_GAME]
            player_stats[bplayer][Vars_idx.NUM_GAME+1:] *= player_stats[bplayer][Vars_idx.NUM_GAME]
            player_stats[wplayer][Vars_idx.NUM_GAME] += 1
            player_stats[bplayer][Vars_idx.NUM_GAME] += 1
            player_stats[wplayer][Vars_idx.NUM_GAME+1] += len(list(game.mainline_moves()))//2
            player_stats[bplayer][Vars_idx.NUM_GAME+1] += len(list(game.mainline_moves()))//2
            
            for move in game.mainline_moves():
                curr_color = board.color_at(move.from_square)
                move_stats, new_king_square = get_move_data(move)

                player_stats[get_color_player(wplayer, bplayer, curr_color)][Vars_idx.NUM_GAME+1:] += move_stats[Vars_idx.NUM_GAME+1:]
                if (new_king_square >= 0):
                    if (curr_color == chess.WHITE):
                        wking_square = move.from_square
                    else:
                        bking_square = move.from_square 
                
                board.push(move)
            
            player_stats[wplayer][Vars_idx.NUM_GAME+1:] /= player_stats[wplayer][Vars_idx.NUM_GAME]
            player_stats[bplayer][Vars_idx.NUM_GAME+1:] /= player_stats[bplayer][Vars_idx.NUM_GAME]            
            game = chess.pgn.read_game(pgn)
            game_idx += 1
            
    with open(f"../training/training_data/player_data_{sys.argv[1]}-{sys.argv[2]}.csv", 'w', newline='') as csvfile:
        player_writer = csv.writer(csvfile, delimiter=',', 
                                   quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        ### Need to write csv headers before stats here:
        for player in player_stats.keys():
            player_writer.writerow([player] + player_stats[player].tolist())

