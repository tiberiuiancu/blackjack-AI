from .utils import busted, blackjack
import numpy as np


class Player:
    def __init__(self, name):
        # list of lists, each representing a hand a player has
        # a player will have more than one set of cards when splitting
        self.cards = []
        self.current_hand = 0
        self.bets = []
        self.name = name

    def reset_cards(self):
        self.cards = [[]]
        self.current_hand = 0

    def make_move(self, **kwargs):
        # will implement in children classes
        pass

    def give_card(self, card):
        if self.current_hand < len(self.cards):
            self.cards[self.current_hand].append(card)

    def can_make_move(self):
        return self.current_hand < len(self.cards)

    def split(self, new_card_1, new_card_2):
        # get current card we want to split
        card_to_split = self.cards[self.current_hand][0]

        # modify current hand
        self.cards[self.current_hand] = [card_to_split, new_card_1]

        # add new hand
        self.cards.append([])
        self.cards[self.current_hand + 1] = [card_to_split, new_card_2]

        # add new bet
        self.bets.append(self.bets[self.current_hand])

    def get_valid_moves(self):
        # we can always stand and hit
        valid_moves = ['stand', 'hit']

        if len(self.cards[self.current_hand]) == 2:
            # we can double if we haven't made any moves yet
            valid_moves.append('double')

            # we can split if the cards are equal
            if self.cards[self.current_hand][0] == self.cards[self.current_hand][1]:
                valid_moves.append('split')

        return valid_moves

    def busted(self):
        return busted(self.cards[self.current_hand])

    def has_blackjack(self):
        return blackjack(self.cards[self.current_hand])


class RandomPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def reset_cards(self):
        super().reset_cards()
        self.bets = [100]

    def make_move(self, **kwargs):
        return np.random.choice(self.get_valid_moves())


class HumanPlayer(Player):
    def __int__(self, name):
        super.__init__(name)

    def reset_cards(self):
        super().reset_cards()
        self.bets = [float(input(self.name + ' AMOUNT TO BET: '))]

    def make_move(self, **kwargs):
        valid_moves = self.get_valid_moves()
        move = ''
        while move not in valid_moves:
            move = input('MOVE: ')

        return move
