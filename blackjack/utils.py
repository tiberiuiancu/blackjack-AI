# A = 0
# 2 = 1
# 3 = 2
# .....
# 10 = 9
# J = 10
# Q = 11
# K = 12


def get_card_value(card):
    if card == 0:
        return 1

    if 1 <= card <= 9:
        return card + 1

    return 10


def get_hand_value(cards):
    return sum([get_card_value(card) for card in cards])


def busted(cards):
    return get_hand_value(cards) > 21


def blackjack(cards):
    if len(cards) != 2:
        return False

    return get_hand_value(cards) == 21


def cards_to_str(cards):
    res = ''
    for card in cards:
        if card == 0:
            res += 'A'
        elif 1 <= card <= 9:
            res += str(card + 1)
        elif card == 10:
            res += 'J'
        elif card == 11:
            res += 'Q'
        else:
            res += 'K'

        res += ' '

    return res