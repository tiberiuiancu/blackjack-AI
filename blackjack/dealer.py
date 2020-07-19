from .utils import busted, has_ace, get_hand_value, blackjack, compare_card_values
import numpy as np
from copy import deepcopy as cp


class Dealer:
    def __init__(self):
        self.cards = []

    def give_card(self, card):
        self.cards.append(card)

    def reset_cards(self):
        self.cards = []

    def make_move(self, **kwargs):
        # will implement in chidlren classes
        pass

    def busted(self):
        return busted(self.cards)


class RandomDealer(Dealer):
    def __init__(self):
        super().__init__()

    def make_move(self, **kwargs):
        return np.random.choice(['stand', 'hit'])


class PerfectDealer(Dealer):
    def __init__(self):
        super().__init__()
        self.cache = {}

    def make_move(self, **kwargs):
        deck = kwargs['deck']
        players = kwargs['players']

        # we can make 2 moves: hit/stand
        # we can directly compute the expected value of stand
        self.cache = {}
        stand_ev = self.stand_expected_value(self.cards, players)
        hit_ev = self.hit_expected_value(cp(self.cards), cp(deck), players)

        if hit_ev == stand_ev:
            return 'stand'
        return 'hit'

    @staticmethod
    def stand_expected_value(cards, players):
        # the stand expected value is just going to be the end of game dealer win amount
        EV = 0
        for player in players:
            for player_cards, bet in zip(player.cards, player.bets):
                # check blackjack
                if blackjack(player_cards) and not blackjack(cards):
                    EV -= bet * 1.5
                    continue

                # check busts
                if busted(player_cards):
                    EV += bet
                elif busted(cards):
                    EV -= bet
                else:
                    # check which value is bigger
                    comparison = compare_card_values(cards, player_cards)
                    if comparison > 0:
                        EV += bet
                    elif comparison < 0:
                        EV -= bet

        return EV

    def hit_expected_value(self, cards, deck, players):
        state = tuple(sorted(cards))

        card_value, ace = get_hand_value(cards), has_ace(cards)

        # cap card_value to 22, so we don't get too many values in the cache
        if card_value > 21:
            card_value = 22

        # if we already have this in the cache, then don't recompute
        if state in self.cache:
            return self.cache[state]

        # we will return the maximum between these 2 values
        EV_hit = 0
        EV_stand = self.stand_expected_value(cards, players)

        # if card value is bigger than 21, we can't hit anymore, so we return the stand EV
        if card_value > 21:
            self.cache[state] = EV_stand
            return self.cache[state]

        # get probability of each card getting drawn
        probs = deck.get_prob()
        for prob, card in zip(probs, range(13)):
            if deck.cards[card] > 0:
                EV_hit += prob * self.hit_expected_value(cp(cards) + [card], deck.draw_card(card), players)

        # some garbage collection since we copy the objects each recursion (??)
        del deck
        del cards

        self.cache[state] = max(EV_hit, EV_stand)
        return self.cache[state]
