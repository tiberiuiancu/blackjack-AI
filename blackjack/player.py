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


class QPlayer(Player):
    def __init__(self, name, training=True):
        super().__init__(name)
        # maps (value, has_ace, dealer_card) to an array [qvalue, n_performed]
        # where n_performed is the number of times the state has occured
        self.qvalues = {}

        # cache for performing the recursive values estimation; same as dealer
        self.move_cache = {}

        # set to true once we don't want to update qtable anymore
        self.training = training

        # a variables which holds the moves made each turn; used to update the qvalues
        self.made_moves = set()

        # epsilon is the random selection value
        self.eps = 1

        # init qvalues
        for value in range(2, 23):
            for ace in [True, False]:
                for dealer_card in range(13):
                    self.qvalues[(value, ace, dealer_card)] = (0, 0)

    def reset_cards(self):
        super().reset_cards()
        self.bets = [1]
        self.made_moves = set()

    def get_valid_moves(self):
        moves = super().get_valid_moves()
        if self.training and 'surrender' in moves:
            moves.remove('surrender')
        return moves

    def get_best_move(self, deck, dealer_card):
        max_ev = -1000
        move_to_make = ''

        cards = self.cards[self.current_hand]
        for move in self.get_valid_moves():
            # get the expected value of making that move in this state
            ev = self.get_expected_value(cards, deck, dealer_card, move)
            if ev > max_ev:
                max_ev = ev
                move_to_make = move

        return move_to_make

    def get_expected_value(self, cards, deck, dealer_card, move):
        hand_value = get_hand_value(cards)
        ace = has_ace(cards)

        if hand_value > 21:
            return -1

        if move == 'stand':
            return self.qvalues[(hand_value, ace, dealer_card)][0]
        elif move == 'hit':
            if (hand_value, ace) in self.move_cache:
                return self.move_cache[(hand_value, ace)]

            ev = 0
            probs = deck.get_prob()
            for p, card in zip(probs, range(13)):
                if p > 0:
                    ev += p * max(
                        self.get_expected_value(cards + [card], deck.draw_card(card), dealer_card, 'stand'),
                        self.get_expected_value(cards + [card], deck.draw_card(card), dealer_card, 'hit'),
                        self.get_expected_value(cards + [card], deck.draw_card(card), dealer_card, 'split')
                    )

            self.move_cache[(hand_value, ace)] = ev
            return ev
        elif move == 'double':
            ev = 0
            probs = deck.get_prob()
            for p, card in zip(probs, range(13)):
                if p > 0:
                    ev += p * self.get_expected_value(cards + [card], deck.draw_card(card), dealer_card, 'stand')
            return ev
        elif move == 'split':
            # because in the 'hit' case we split without checking if it is possible, we check here
            if len(cards) != 2 or cards[0] != cards[1]:
                return -1000
            return 2 * self.get_expected_value(cards[:-1], deck, dealer_card, 'hit')
        elif move == 'surrender':
            return -0.5

    def make_move(self, **kwargs):
        dealer_card = kwargs['dealer_card']
        deck = kwargs['deck']
        cards = self.cards[self.current_hand]

        # reset move cache
        self.move_cache = {}

        if self.training:
            # pick random move with prob eps
            if np.random.rand() < self.eps:
                move = np.random.choice(self.get_valid_moves())
            else:
                move = self.get_best_move(deck, dealer_card)

            state = (get_hand_value(cards), has_ace(cards), dealer_card)
            self.made_moves.add(state)
            return move
        else:
            return self.get_best_move(deck, dealer_card)

    def update_q(self, reward):
        for state in self.made_moves:
            qvalue, n = self.qvalues[state]

            # qvalue is the average of n_played values
            # to make it the average of n + 1 values, we have to multiply by n / (n + 1)
            # and then add the reward * (n + 1)
            qvalue *= n / (n + 1)
            qvalue += reward / (n + 1)

            # update qvalues
            self.qvalues[state] = (qvalue, n + 1)
