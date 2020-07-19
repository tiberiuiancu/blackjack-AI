from blackjack import *

if __name__ == '__main__':
    g = Game(players=[HumanPlayer('p1')], dealer_type=PerfectDealer)

    g.start_round()

