# pgn_parser.py, get_move_data():

The purpose of this script is to extract PGNs from TWIC ZIP files, parse the games in each .pgn file for features of the game that I've selected (detailed in pgn_parser.py), and send that data to a new .csv datafile for the style learning model.

## Dataset Setup note: 
- Save twic datasets in the twic_datasets directory. They can still be in zip files if you prefer.
- Save output datasets to the path: ../training/train_datasets
- Load input pgn data from ./twic_datasets
- Call in terminal using python pgn_parser.py <first file number> <last file number>

# Prototype History:
## Prototype 2 (3/29/26): Collects all (9) manual variables on original datasets for each player
## Prototype 1 (3/23/26): First implementation, gets info on piece/pawn positioning + preliminary piece directional info