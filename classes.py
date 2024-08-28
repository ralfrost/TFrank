from datetime import date


RANK_MIN = 3
NEW_PLAYER_STATUS_LIMIT = 8
MAX_POINTS = 30

def mean(list) -> float:
    return sum(list)/len(list)

class Match:

    def __init__(self, match_player_ids, zero_game_wt, zero_game_lt) -> None:
        self.match_player_ids = match_player_ids
        self.zero_game_wt = zero_game_wt
        self.zero_game_lt = zero_game_lt

class _Player:

    def __init__(self, id, alias) -> None:
        self.id = id
        self.alias = alias
        self.rank = 500
        self.win = 0
        self.loss = 0
        self.zero_win = 0
        self.zero_loss = 0
        self.games = 0
        # self.game_stats = {'avg_diff': {}, 'win':{}, 'loss':{}, 'zero_win': {}, 'zero_loss': {}}
        self.ranked_games = 0
        self.unranked = True
        self.active = True
        self.last_played_date = date(1989,11,9)
        self.placement_matches = []

    def __str__(self):
        return self.id
    
    def __repr__(self):
        return self.id

    def print(self) -> None:
        if self.unranked:
            print(f'{self.id} alias \"{self.alias}\" is unranked. ({RANK_MIN - len(self.placement_matches)} matches until ranked)')
        else:
            print(f'{self.id} alias \"{self.alias}\" has rank {round(self.rank)}.')


    def rank_player(self) -> None:
    # We can use the sum of the enemy ranks minus the rank of the teammate we get bounds for the rank of the to-be-ranked player. 
    # If the game was won the value gives a lower bound if lost an upper bound.
    # If all upper and lower bounds result in one interval the value closest to 500 of the interval is taken as rank.
    # Otherwise the average of all contradicting bounds is taken.
    # As the match results affect the rank a second time, when they are evaluated, the rank is limited between 300 and 700.
 
        self.unranked = False

        win_diff = []
        loss_diff = []
        # calculate team rank diff and determine wins and losses
        for [players, zero_game_wt, zero_game_lt] in self.placement_matches:
            match players.index(self):  
                case 0:
                    diff_val=players[2].rank + players[3].rank - players[1].rank
                    win_diff.append(diff_val)
                case 1:
                    diff_val=players[2].rank + players[3].rank - players[0].rank
                    win_diff.append(diff_val)
                case 2:
                    diff_val=players[0].rank + players[1].rank - players[3].rank
                    loss_diff.append(diff_val)
                case 3:
                    diff_val=players[0].rank + players[1].rank - players[3].rank
                    loss_diff.append(diff_val)
        
        win_diff.sort(reverse=True)
        loss_diff.sort()

        if len(loss_diff) == 0:
            self.rank = min(max(win_diff[0], 500), 700)
        elif len(win_diff) == 0:
            self.rank = max(min(loss_diff[0], 500), 300)
        elif win_diff[0] <= loss_diff[0]:
            if 500 < win_diff[0]:
                self.rank = min(win_diff[0], 700)
            elif 500 > loss_diff[0]:
                self.rank = max(loss_diff[0], 300)
            else:
                self.rank = 500 # when 500 is inside bounds, set rank to 500
        else:
            rdiffs = [] # relevant diffs
            min_len = min(len(win_diff), len(loss_diff))
            for i in range(min_len):
                if win_diff[i] > loss_diff[i]:
                    rdiffs.append(win_diff[i])
                    rdiffs.append(loss_diff[i])
                else: break

            if win_diff[i] > mean(rdiffs):
                rdiffs.append(win_diff[i])

                for j in range(i+1,len(win_diff)):
                    if win_diff[j] > mean(rdiffs):
                        rdiffs.append(win_diff[j])
                    else: break
            else:
                for j in range(i,len(loss_diff)):
                    if loss_diff[j] < mean(rdiffs):
                        rdiffs.append(loss_diff[j])
                    else: break

            self.rank = max(min(mean(rdiffs), 700), 300)


    def update_rank(self, team_winchance, win, zero_game_wt, zero_game_lt) -> None:
        # Should prevent players' rank exceeding 0 or 1000. Apply only if for increasing rank when rank greater than 500 or for decreasing when already lower then 500        
        if (win and self.rank > 500) or (not win and self.rank < 500):
            damp = (1 - (1/499.9*(self.rank - 500))**6)
        else:
            damp = 1
        
        # rank should only change significantly if winning team's rank is not more than 50 greater than losing team's rank
        if self.ranked_games < NEW_PLAYER_STATUS_LIMIT:
            j = 2*MAX_POINTS
        else: 
            j = MAX_POINTS
            
        if win:
            k = j*(1-team_winchance)
        else:
            k = -j*team_winchance
        # double rank changes if losing team lost with zero goals
        c=1
        if zero_game_wt:
            c=2*c
        if zero_game_lt:
            c=0.5*c
        
        update_points = c*damp*k
        
        self.rank = self.rank + update_points
        print(f'{self.alias}: {round(self.rank)}(+{round(update_points)})')

        
class RankData:

    def __init__(self) -> None:
        self.players = []
        self.unrankable_matches = []
        self.game_stats = {}

    def add_player(self, player_id, alias) -> None:
        if self.get_player(player_id) is None:
            player = _Player(player_id, alias)
            self.players.append(player)
        else: 
            print('A Player with this id already exists. Please choose another id.')


    def del_player(self, player_id) -> None:
        player = self.get_player(player_id)
        self.players.remove(player)
        print(f'Player {player_id} was successfully deleted.')

    
    def list_players(self) -> None:
        player_sort=sorted(self.players, key=lambda player: player.id, reverse=False)
        print(f'{"ID" : <5}{"Alias" : <16}{"Status" : <9}{"Last played" : <11}')
        for player in player_sort:
            if player.unranked:
                print(f'{player.id : <5}{player.alias : <16}{"unranked" : <9}{player.last_played_date.isoformat(): <11}')
            else:
                print(f'{player.id : <5}{player.alias : <16}{"ranked" : <9}{player.last_played_date.isoformat(): <11}')


    def print_ranking(self, eternal) -> None:
        player_sort=sorted(self.players, key=lambda player: player.rank, reverse=True)
        # Only ranked players appear in ranking
        player_red=[player for player in player_sort if not player.unranked]
        
        if not eternal:
            player_red=[player for player in player_red if player.active and ((date.today() - player.last_played_date).days < 180)]

        print(f'{"Ranking" : <20}{"Points" : ^8}{"Win/Loss" : ^11}{"Z_Win/Z_Loss" : ^13}{"WR" : <5}')
        
        for i in range(len(player_red)):
            if i == 0:
                rank = 1
            elif round(player_red[i].rank) < round(player_red[i-1].rank):
                rank = i+1

            if player_red[i].win == 0:
                wr = 0
            elif player_red[i].loss == 0:
                    wr = 'droelf' #float('inf')
            else:
                wr = round(player_red[i].win/player_red[i].loss, 2)

            print(f'{rank :>2}. {player_red[i].alias :<16}{round(player_red[i].rank) :^8}{player_red[i].win :>4}/{player_red[i].loss: <7}{player_red[i].zero_win :>4}/{player_red[i].zero_loss :<7}{wr :<5}')


    def _unranked_players(self, players) -> int:
        unranked_players = []

        for player in players:
            if player.unranked:
                unranked_players.append(player)
        return  unranked_players
    

    def get_player(self, player_id) -> _Player:
        for player in self.players:
            if player.id == player_id:
                return player
        return None


    def _get_players(self, player_ids) -> list[_Player]:
        players = []
        for player_id in player_ids:
            players.append(self.get_player(player_id))
        return players


    def add_match(self, match, match_date=date.today(), new=True) -> bool:
        
        # Get player objects
        match_players = self._get_players(match.match_player_ids)

        for player in match_players:
            player.last_played_date = match_date

        
        # Check for unranked players
        unranked_players = self._unranked_players(match_players)
        
        if new:
            self._update_match_stats(match_players, match.zero_game_wt, match.zero_game_lt)

        if len(unranked_players) == 0:
            self._rank_match(match_players, match.zero_game_wt, match.zero_game_lt)
            return True
        elif len(unranked_players) > 1:
            print(f'More then one unranked players {unranked_players} took part in this match. The match is stored for later evaluation.')
            self.unrankable_matches.append(match)
            return True 
        elif len(unranked_players) == 1:
            unranked_players[0].placement_matches.append([match_players, match.zero_game_wt, match.zero_game_lt])
            unranked_players[0].print()
            
            if len(unranked_players[0].placement_matches) < RANK_MIN:
                return True
            else: # player has played enough matches to get ranked
                unranked_players[0].rank_player()
                print(f'Congratulations, {unranked_players[0].alias} was ranked!')
                # update ranks according to placement_matches
                for [match_player, zero_game_wt, zero_game_lt] in unranked_players[0].placement_matches:
                    self._rank_match(match_player, zero_game_wt, zero_game_lt)
                
                print('Checking unrankable matches...')
                for unrankable_match in self.unrankable_matches:
                    self.unrankable_matches.remove(unrankable_match)
                    print(f'Trying to rank match: {unrankable_match.match_player_ids}')
                    self.add_match(unrankable_match, new=False)
                return True
                

    def _update_match_stats(self, match_player, zero_game_wt, zero_game_lt) -> None:
        # Update player stats
        for i in range(4):
            match_player[i].games += 1
            if i in [0,1]:
                match_player[i].win += 1
            if i in [2,3]:
                match_player[i].loss += 1
        if zero_game_wt:
            match_player[0].zero_win += 1
            match_player[1].zero_win += 1
            match_player[2].zero_loss += 1
            match_player[3].zero_loss += 1
        if zero_game_lt:
            match_player[2].zero_win += 1
            match_player[3].zero_win += 1
            match_player[0].zero_loss += 1
            match_player[1].zero_loss += 1

    def _update_ranked_match_stats(self, match_player, zero_game_wt, zero_game_lt, team_diff) -> None:
        for i in range(4):
            match_player[i].games += 1
            if i in [0,1]:
                match_player[i].win += 1
            if i in [2,3]:
                match_player[i].loss += 1
        if zero_game_wt:
            match_player[0].zero_win += 1
            match_player[1].zero_win += 1
            match_player[2].zero_loss += 1
            match_player[3].zero_loss += 1
        if zero_game_lt:
            match_player[2].zero_win += 1
            match_player[3].zero_win += 1
            match_player[0].zero_loss += 1
            match_player[1].zero_loss += 1        

    def _team_rank(self, player1_rank, player2_rank) -> int:
        player_rank = [player1_rank, player2_rank]
        k = [0,0]
        for i in [0,1]:
            if player_rank[i] < 500:
                k[i]=1
            else:
                k[i] = 1+3*((player_rank[i]-500)/500)**7

        #team_rank = round(2*(k[0]*player_rank[0]+k[1]*player_rank[1])/(k[0]+k[1]))
        team_rank = (player_rank[0]+player_rank[1])
        return team_rank

    def _rank_match(self, match_player, zero_game_wt, zero_game_lt) -> None:
        # Calculate team_rank values and team_diff
        team1_rank = self._team_rank(match_player[0].rank, match_player[1].rank)
        team2_rank = self._team_rank(match_player[2].rank, match_player[3].rank)
        
        team1_winchance = 1/(1+10**((team2_rank - team1_rank)/350)) 
        team2_winchance = 1/(1+10**((team1_rank - team2_rank)/350))
        # print(f'Result: {match_player[0]}. {match_player[1]}, {match_player[2]}, {match_player[3]}')
        # print(f'Ranks: {match_player[0].rank}. {match_player[1].rank}, {match_player[2].rank}, {match_player[3].rank}')
        
        # Calculate new ranks
        for i in [0,1]:
            match_player[i].update_rank(team1_winchance, True, zero_game_wt, zero_game_lt)
            match_player[i].ranked_games += 1
            # for j in [2,3]:
            #     try:
            #         wins = self.game_stats[match_player[i].id][match_player[j].id]['wins']
            #         avg_diff = self.game_stats[match_player[i].id][match_player[j].id]['avg_diff']
            #         new_avg_diff = (wins*avg_diff + team_diff) / (wins+1)
            #         self.game_stats[match_player[i].id][match_player[j].id]['wins'] += 1
            #         self.game_stats[match_player[i].id][match_player[j].id]['avg_diff'] = new_avg_diff
            #     except KeyError:
            #         try:
            #             self.game_stats[match_player[i].id][match_player[j].id] = {'wins':1, 'avg_diff':team_diff}
            #         except:
            #             self.game_stats[match_player[i].id] = {match_player[j].id : {'wins':1, 'avg_diff':team_diff}}
                # print(f'{match_player[i].id}>{match_player[j].id} {self.game_stats[match_player[i].id][match_player[j].id]}')
        
        for i in [2,3]:
            match_player[i].update_rank(team2_winchance, False, zero_game_wt, zero_game_lt)
            match_player[i].ranked_games += 1
        
