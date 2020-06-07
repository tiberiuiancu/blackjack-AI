from .utils import busted, blackjack, has_ace, get_hand_value
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
        return self.current_hand < len(self.cards) and self.cards[0]

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

        if len(self.cards[self.current_hand]) == 2 and len(self.cards) == 1:
            # we can double and surrender if we haven't made any moves yet
            valid_moves.append('double')
            valid_moves.append('surrender')

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
        super().__init__(name)

    def reset_cards(self):
        super().reset_cards()
        self.bets = [float(input(self.name + ' AMOUNT TO BET: '))]

    def make_move(self, **kwargs):
        valid_moves = self.get_valid_moves()
        move = ''
        while move not in valid_moves:
            move = input('MOVE: ')

        return move


# class TablePlayer(Player):
#     # talbe from https://www.quora.com/Is-there-a-difference-between-the-game-of-Blackjack-and-21
#     def __int__(self, name):
#         super().__init__(name)
#
#     def reset_cards(self):
#         super().reset_cards()
#         self.bets = [100]
#
#     def make_move(self, **kwargs):
#         dealer_card = kwargs['dealer_card']
#
#         cards = self.cards[self.current_hand]
#         valid_moves = self.get_valid_moves()
#
#         # implement edge cases:
#         if len(cards) == 2:
#             # case where player has ACE
#             if has_ace(cards):
#                 # A 2 | A 3
#                 if 1 in cards or 2 in cards:
#                     if (4 <= dealer_card <= 5) and 'double' in valid_moves:
#                         return 'double'
#                     return 'hit'
#
#                 # A 4 | A 5
#                 if 3 in cards or 4 in cards:
#                     if (3 <= dealer_card <= 5) and \
#                             'double' in valid_moves:
#                         return 'double'
#                     return 'hit'
#
#                 # A 6
#                 if 5 in cards:
#                     if 3 <= dealer_card <= 6 and 'double' in valid_moves:
#                         return 'double'
#                     else:
#                         return 'hit'
#
#                 # A 7
#                 if 6 in cards:
#                     if 3 <= dealer_card <= 6:
#                         if 'double' in valid_moves:
#                             return 'double'
#                         else:
#                             return 'hit'
#                     elif dealer_card == 1 or 6 <= dealer_card <= 7:
#                         return 'stand'
#                     else:
#                         return 'hit'
#
#                 # A 7 | A 8 | A 9
#                 return 'stand'
#
#             if cards[0] == cards[1]:
#                 # 2 2 | 3 3
#                 if cards[0] == 1 or cards[0] == 2:
#                     if 3 <= dealer_card <= 6:
#                         return 'split'
#                     else:
#                         return 'hit'
#
#                 # 4 4
#                 if cards[0] == 3:
#                     return 'hit'
#
#                 # 5 5
#                 if cards[0] == 4:
#                     if 1 <= dealer_card <= 8 and 'double' in valid_moves:
#                         return 'double'
#                     else:
#                         return 'hit'
#
#                 # 6 6
#                 if cards[0] == 5:
#                     if 2 <= dealer_card <= 5:
#                         return 'split'
#                     else:
#                         return 'hit'
#
#                 # 7 7
#                 if cards[0] == 6:
#                     if 1 <= dealer_card <= 6:
#                         return 'split'
#                     else:
#                         return 'hit'
#
#                 # 8 8
#                 if cards[0] == 7:
#                     return 'split'
#
#                 # 9 9
#                 if cards[0] == 8:
#                     if 1 <= dealer_card <= 5 or 7 <= dealer_card <= 8:
#                         return 'split'
#                     else:
#                         return 'stand'
#
#                 # 10 10
#                 if cards[0] == 9:
#                     return 'stand'
#
#                 # A A
#                 if cards[0] == 0:
#                     return 'split'
#
#         card_value = get_hand_value(cards)
#
#         # case where you have a big sum
#         if card_value >= 17:
#             return 'stand'
#
#         ace = has_ace(cards)
#         if ace and 21 >= card_value + 10 >= 17:
#             return 'stand'
#
#         if not ace and card_value <= 8:
#             return 'hit'


class QPlayer(Player):
    def __init__(self, name, training=True):
        super().__init__(name)
        # maps (value, has_ace, dealer_card, move) to an array [qvalue, n_performed]
        # where n_performed is the number of times the state has occured
        self.qvalues = {}

        # set to true once we don't want to update qtable anymore
        self.training = training

        # a variables which holds the moves made each turn; used to update the qvalues
        self.made_moves = set()

        # epsilon is the random selection value
        self.eps = 0.5

        # init qvalues
        for value in range(2, 23):
            for ace in [True, False]:
                for dealer_card in range(13):
                    for move in ['hit', 'stand', 'double', 'split', 'surrender']:
                        self.qvalues[(value, ace, dealer_card, move)] = (0, 0)

    def reset_cards(self):
        super().reset_cards()
        self.bets = [1]
        self.made_moves = set()

    def get_best_move(self, dealer_card):
        max_score = -1000
        move_to_make = ''

        hand_value = get_hand_value(self.cards[self.current_hand])
        ace = has_ace(self.cards[self.current_hand])
        for move in self.get_valid_moves():
            state = self.qvalues[(hand_value, ace, dealer_card, move)]
            if state[0] > max_score:
                max_score = state[0]
                move_to_make = move

        return move_to_make

    def make_move(self, **kwargs):
        dealer_card = kwargs['dealer_card']

        if self.training:
            # pick random move with prob eps
            if np.random.rand() < self.eps:
                move = np.random.choice(self.get_valid_moves())
            else:
                move = self.get_best_move(dealer_card)

            state = (get_hand_value(self.cards[self.current_hand]),
                     has_ace(self.cards[self.current_hand]), dealer_card, move)
            self.made_moves.add(state)
            return move
        else:
            return self.get_best_move(dealer_card)

    def update_q(self, reward):
        for state in self.made_moves:
            qvalue, n = self.qvalues[state]
            print(n)

            # qvalue is the average of n_played values
            # to make it the average of n + 1 values, we have to multiply by n / (n + 1)
            # and then add the reward * (n + 1)
            qvalue *= n / (n + 1)
            qvalue += reward / (n + 1)

            # updaate qvalues
            self.qvalues[state] = (qvalue, n + 1)
