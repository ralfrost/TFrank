#!/usr/bin/env python3

import argparse
import pickle
import sys

from classes import *

# Manually set the ranking value of one or all players to a specific value and set status to ranked
# Usage: ./TFedit.py <playerid>|all <rank>

if __name__ == '__main__':

    with open('data.pickle', 'rb') as data_file:
        data = pickle.load(data_file)

    player_id = sys.argv[1]

    if player_id == 'del':
        player = data.get_player(sys.argv[2])
        data.players.remove(player)
    else:
        ranking_value = int(sys.argv[2])

        if player_id == 'all':
            for player in data.players:
                player.rank = ranking_value
                player.unranked = False
        else:
            data.rank = ranking_value
            data.unranked = False

    with open('data.pickle', 'wb') as data_file:
                pickle.dump(data, data_file)
