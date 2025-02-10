#!/usr/bin/env python3

import argparse
import csv
from datetime import date
import pickle
import sys
import os
from threading import Thread

from classes import *

DATA_FILE = 'data.pickle'
HISTORY_FILE = 'results.csv'

def prompt_match_info(data):
    while True:
        match_player_ids = []
        for i in [1,2]:
            match_player_ids.append(input(f'Winning team: Id of Player {i}: '))
            if data.get_player(match_player_ids[i-1]) is None:
                print(f'{match_player_ids[i-1]} is not yet registered. Please register player first.')
                exit()

        for i in [1,2]:
            match_player_ids.append(input(f'Losing team: Id of Player {i}: '))
            if data.get_player(match_player_ids[2+i-1]) is None:
                print(f'{match_player_ids[2+i-1]} is not yet registered. Please register player first.')
                exit()
        if confirm('Did any team loose a game with zero goals?'):
            zero_game_wt = confirm('Did the loosing team loose a game with zero goals?')
            zero_game_lt = confirm('Did the winning team loose a game with zero goals?')
            # Makes the programm run in to a loop. Not yet fixed.
            # if zero_game_wt:
            #    if confirm('Did the loosing team loose two games with zero goals?'):
            #         music_thread = Thread(target=play_hundi)
            #         music_thread.start()
        else:
            zero_game_wt = False
            zero_game_lt = False

        if zero_game_wt or zero_game_lt:  
            if confirm(f'So {match_player_ids[0]} won with {match_player_ids[1]} against {match_player_ids[2]} and {match_player_ids[3]} and at least one team lost with zero goals?'):
                break
        else:
            if confirm(f'So {match_player_ids[0]} won with {match_player_ids[1]} against {match_player_ids[2]} and {match_player_ids[3]} and no team lost with zero goals?'):
                break

    return [match_player_ids, zero_game_wt, zero_game_lt]

def play_hundi():
    os.system('xdg-open hundi.mp3')

def prompt_player_info():
    while True:
        player_id = input('First four letters of player\'s first name: ')
        if len(player_id) == 4:
            break
    while True:
        alias = input('Player\'s alias to appear in ranking table: ')
        if len(alias) <= 20:
            break
    return [player_id, alias]


def prompt_new_alias(player):
    new_alias = input('New alias: ')
    if not confirm(f'So you want to change alias from {player.alias} to {new_alias}?'):
        exit()
    return new_alias

        
def confirm(s='Do you want to apply changes?'):
    while True:
        confirm = input(s + ' [y/n]: ')
        if confirm == 'y':
            return True
        if confirm == 'n':
            return False

def load_data():
    try:
        with open(DATA_FILE, 'rb') as data_file:
            return pickle.load(data_file)
    except: 
        print(f'Couldn\'t load data. Make sure {DATA_FILE} file exists in project root directory or add new player in order to create new data file.')
        exit()


def load_or_create_data():
    try:
        with open(DATA_FILE, 'rb') as data_file:
            return pickle.load(data_file)
    except:
        if confirm('Couldn\'t load data. Do you want to create a new data file?'):
            return RankData()
        else: 
            print('Exiting program.')
            exit()


def write_data(data):
    with open(DATA_FILE, 'wb') as data_file:
        pickle.dump(data, data_file)


def write_history(match, match_date=None):
    match_player_ids = match.match_player_ids
    zero_game_wt = match.zero_game_wt
    zero_game_lt = match.zero_game_lt
    if match_date is None:
        match_date = date.today().isoformat()

    with open(HISTORY_FILE, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([match_player_ids[0], match_player_ids[1], match_player_ids[2], match_player_ids[3], zero_game_wt, zero_game_lt, match_date])
    

banner = r'''
 
    /^\                                     
    \_/                                     
   / V \______________               _      
  =| o |__   __|  ____|=============| |===
   \|_|/  | |  | |__ _ __ __ _ _ __ | | _   
   {/ \}  | |  |  __| '__/ _` | '_ \| |/ /   
    |_|   | |  | |  | | | (_| | | | |   <    
    |^|   |_|  |_|  |_|  \__,_|_| |_|_|\_\   
    |||      _                               
   [_X_]    (_)         by El Ruedi v1.2.0
'''

if __name__ == '__main__':
    print(banner)

    parser = argparse.ArgumentParser('./TFrank.py', description='TFrank implements a ranking system for table football matches similar to the ELO system.')

    parser.add_argument('-a',
                        '--add',
                        action = 'store_true',
                        help = 'Add new player')
    parser.add_argument('-b',
                        '--batch_add',
                        metavar = 'PLAYERS.csv',
                        help = 'Add batch of new players from .csv file')
    parser.add_argument('-c',
                        '--change_alias',
                        metavar = 'PLAYER_ID',
                        help = 'Change player alias')
    parser.add_argument('--delete',
                        metavar='PLAYER_ID',
                        help = 'Delete player')
    parser.add_argument('-d',
                        '--deactivate',
                        metavar='PLAYER_ID',
                        help = 'Flag player als inactive')
    parser.add_argument('-e',
                        '--eternal',
                        action = 'store_true',
                        help = 'Show eternal ranking table')
    parser.add_argument('-i',
                        '--history',
                        metavar = 'HISTORY.csv',
                        help = 'Import match history from .csv file.')
    parser.add_argument('-l',
                        '--list',
                        action = 'store_true',
                        help = 'List all registered players.')
    parser.add_argument('-m', 
                        '--match',
                        action = 'store_true',
                        help = 'Add new match results.')
    parser.add_argument('-p',
                        '--player',
                        metavar = 'PLAYER_ID',
                        help = 'Get rank of player by player id.')
    parser.add_argument('-r',
                        '--rank',
                        action = 'store_true',
                        help = 'Show current ranking table.')
                        
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    if args.add:
        data = load_or_create_data()
        [player_id, alias] = prompt_player_info()
        data.add_player(player_id, alias)
        write_data(data)
    
    if args.batch_add is not None:
        data = load_or_create_data()
        
        with open(args.batch_add, 'r', newline='') as csv_file:
            reader = csv.reader(csv_file)

            for [player_id, alias] in reader:
                if player_id != "ID": 
                    data.add_player(player_id, alias)
                    print(f'Added player {player_id} aka {alias}.')
        write_data(data)


    if args.change_alias is not None:
        player_id = args.change_alias
        data = load_data()
        player = data.get_player(player_id)
        if player is None:
            print(f'{player_id} is not registered, check for correct spelling.')
        else: 
            new_alias = prompt_new_alias(player)
            player.alias = new_alias
        write_data(data)
        exit()    

    if args.delete:
        player_id = args.delete
        data = load_data()
        player = data.get_player(player_id)
        if player is None:
            print(f'{player_id} is not registered, check for correct spelling.')
        else: 
            if confirm(f'Do you really want to delete player {player_id} alias {player.alias}?'):
                data.del_player(player_id)
            else:
                exit()
        write_data(data)
        exit()    

    if args.deactivate:
        player_id = args.deactivate
        data = load_data()
        player = data.get_player(player_id)
        if player is None:
            print(f'{player_id} is not registered, check for correct spelling.')
        else: 
            if confirm(f'Do you really want to deactivate player {player_id} alias {player.alias}?'):
                player.active = False
            else:
                exit()
        write_data(data)
        exit()    

    if args.rank:
        data = load_data()
        data.print_ranking(eternal=False)
        exit()

    if args.eternal:
        data = load_data()
        data.print_ranking(eternal=True)
        exit()

    if args.list:
        data = load_data()
        data.list_players()
        exit()

    if args.match:
        data = load_data()
        match_data = prompt_match_info(data)
        match = Match(match_data[0],match_data[1],match_data[2])
        if data.add_match(match):
            write_history(match)
            write_data(data)
        else:
            exit()

    if args.player is not None:
        player_id = args.player
        data = load_data()
        player = data.get_player(player_id)
        if player is None:
            print(f'{player_id} is not registered, check for correct spelling.')
        else: 
            player.print()
        exit() 

    if args.rank:
        data = load_data()
        data.print_ranking(eternal=False)
        exit()

    if args.history is not None:
        data = load_data()
        with open(args.history, 'r', newline='') as csv_file:
            reader = csv.reader(csv_file)

            line_count = 0
            for row in reader:
                if line_count != 0: 
                    match_player_ids = row[0:4]
                    zero_game_wt = (row[4] == 'True')
                    zero_game_lt = (row[5] == 'True')
                    match_date = row[6]
                    match = Match(match_player_ids, zero_game_wt, zero_game_lt)
                    print(f'Importing match: {match_player_ids}, {zero_game_wt}, {zero_game_lt}, {match_date}')
                    data.add_match(match, match_date=date.fromisoformat(match_date))
                    write_history(match, match_date)
                line_count = line_count + 1
        write_data(data)
        # except: 
            # print('Couldn\'t find history. Make sure \'results.csv\' exists in base directory.')
