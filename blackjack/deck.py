import numpy as np


class Deck:
    def __init__(self, n_decks):
        # because the color doesn't matter, we consider the a deck to have 13 cards
        self.n_decks = n_decks
        self.cards = []
        self.reset()

    def draw_card(self, card=None):
        if card is not None:
            if self.cards[card] > 0:
                self.cards[card] -= 1
        else:
            # get probability of each card
            total = sum(self.cards)
            probs = [card/total for card in self.cards]
            return np.random.choice([i for i in range(13)], p=probs)

    def reset(self):
        self.cards = [self.n_decks * 4 for _ in range(13)]
