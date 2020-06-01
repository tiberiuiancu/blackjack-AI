# we want to collect the following stats:
# -losses/wins of players and dealer
# -moves made given a certain hand


class Collector:
    def __init__(self):
        # NOTE: dealer's name is 'dealer' in the dicts below
        # maps player names to a list of their rewards
        self.rewards = {}

        # maps player names to a list of moves of format ((card1, card2,...), 'move')
        self.moves = {}

    def add_move(self, player_name, cards, move):
        if player_name not in self.moves:
            self.moves[player_name] = []
        self.moves[player_name] += [(tuple(cards), move)]

    def add_reward(self, player_name, reward):
        if player_name not in self.rewards:
            self.rewards[player_name] = []
        self.rewards[player_name] += [reward]
