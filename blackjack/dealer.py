from .utils import busted
import numpy as np


class Dealer:
    def __init__(self):
        self.cards = []

    def give_card(self, card):
        self.cards.append(card)

    def reset_cards(self):
        self.cards = []

    def make_move(self, players):
        # will implement in chidlren classes
        pass

    def busted(self):
        return busted(self.cards)


class RandomDealer(Dealer):
    def __init__(self):
        super().__init__()

    def make_move(self, players):
        return np.random.choice(['stand', 'hit'])
