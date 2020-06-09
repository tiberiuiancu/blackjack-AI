import numpy as np

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


def has_ace(cards):
    for card in cards:
        if card == 0:
            return True

    return False


def compare_card_values(cards1, cards2):
    ace1 = has_ace(cards1)
    ace2 = has_ace(cards2)

    cards1_value = get_hand_value(cards1)
    if ace1 and cards1_value + 10 <= 21:
        cards1_value += 10

    cards2_value = get_hand_value(cards2)
    if ace2 and cards2_value + 10 <= 21:
        cards2_value += 10

    return cards1_value - cards2_value


def get_random_cards():
    hand_value = np.random.randint(2, 22)
    has_ace = bool(np.random.randint(0, 2))

    if hand_value == 2 or hand_value == 2 and not has_ace:
        return get_random_cards()

    cards = []
    if has_ace:
        cards.append(0)
        hand_value -= 1

    # greedily give player some cards that amount to hand_value
    while hand_value > 0:
        # if the player doesn't have an ace, we must give them a 2 and an 9 to amount to 11
        if hand_value == 11 and not has_ace:
            cards.append(1)
            cards.append(8)
            break

        # if the hand value is at least 10, give them player a 10 and continue
        if hand_value > 10:
            cards.append(9)
            hand_value -= 10
            continue

        # if the hand value is less or eq to 10, give them the biggest card we can and exit
        if len(cards):
            cards.append(hand_value - 1)
            break

        # if the player has no cards currently, we split the remaining value in 2
        card1 = hand_value // 2
        card2 = hand_value - card1
        cards.append(card1 - 1)
        cards.append(card2 - 1)

    return cards
