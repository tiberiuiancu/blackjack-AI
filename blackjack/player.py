from .utils import busted, blackjack, has_ace
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


class TablePlayer(Player):
    # talbe from https://www.quora.com/Is-there-a-difference-between-the-game-of-Blackjack-and-21
    def __int__(self, name):
        super().__init__(name)

    def reset_cards(self):
        super().reset_cards()
        self.bets = [100]

    def make_move(self, **kwargs):
        dealer_card = kwargs['dealer_card']

        cards = self.cards[self.current_hand]
        valid_moves = self.get_valid_moves()

        # implement edge cases:
        if len(cards) == 2:
            # case where player has ACE
            if has_ace(cards):
                # A 2 | A 3
                if 1 in cards or 2 in cards:
                    if (4 <= dealer_card <= 5) and 'double' in valid_moves:
                        return 'double'
                    return 'hit'

                # A 4 | A 5
                if 3 in cards or 4 in cards:
                    if (3 <= dealer_card <= 5) and \
                            'double' in valid_moves:
                        return 'double'
                    return 'hit'

                # A 6
                if 5 in cards:
                    if 3 <= dealer_card <= 6 and 'double' in valid_moves:
                        return 'double'
                    else:
                        return 'hit'

                # A 7
                if 6 in cards:
                    if 3 <= dealer_card <= 6:
                        if 'double' in valid_moves:
                            return 'double'
                        else:
                            return 'hit'
                    elif dealer_card == 1 or 6 <= dealer_card <= 7:
                        return 'stand'
                    else:
                        return 'hit'

                # A 7 | A 8 | A 9
                return 'stand'

            if cards[0] == cards[1]:
                # 2 2 | 3 3
                if cards[0] == 1 or cards[0] == 2:
                    if 3 <= dealer_card <= 6:
                        return 'split'
                    else:
                        return 'hit'

                # 4 4
                if cards[0] == 3:
                    return 'hit'

                # 5 5
                if cards[0] == 4:
                    if 1 <= dealer_card <= 8 and 'double' in valid_moves:
                        return 'double'
                    else:
                        return 'hit'

                # 6 6
                if cards[0] == 5:
                    if 2 <= dealer_card <= 5:
                        return 'split'
                    else:
                        return 'hit'

                # 7 7
                if cards[0] == 6:
                    if 1 <= dealer_card <= 6:
                        return 'split'
                    else:
                        return 'hit'

                # 8 8
                if cards[0] == 7:
                    return 'split'

                # 9 9
                if cards[0] == 8:
                    if 1 <= dealer_card <= 5 or 7 <= dealer_card <= 8:
                        return 'split'
                    else:
                        return 'stand'

                # 10 10
                if cards[0] == 9:
                    return 'stand'

                # A A
                if cards[0] == 0:
                    return 'split'
