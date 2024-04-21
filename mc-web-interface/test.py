
def check_player_change(sold_players, scurrent_players):
        current_players = scurrent_players
        sold = sorted(sold_players)

        if current_players == sold:
            return
        if len(current_players) == 0:
            return
        
        if len(current_players) > len(sold_players):
            new_players = set(current_players) - set(sold_players)
            print(f'{new_players} joined the Game.')
            sold_players = current_players
        
        elif len(current_players) < len(sold_players):
            left_players = set(sold_players) - set(current_players)
            print(f'{left_players} left the Game.')
            sold_players = current_players
        # Same length different players
        elif len(current_players) == len(sold_players):
            intersection = set(current_players).intersection(set(sold_players))
            if intersection == []:
                print('intersection is empty')
                print(f'{sold_players} left the Game.')
                print(f'{current_players} joined the Game.')
                sold_players = current_players
            else:
                left = list(set(sold_players) - set(current_players))
                joined = list(set(current_players) - set(sold_players))
                print(f'{left} left the Game.')
                print(f'{joined} joined the Game.')
                

check_player_change(['A', 'b', 'C', 'D'], ['Z', 'X', 'F', 'E'])
