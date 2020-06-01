from blackjack.game import Game
from blackjack.player import *
from blackjack.dealer import *
import numpy as np

np.random.seed(0)

N_ROUNDS = 100

if __name__ == '__main__':
    players = [RandomPlayer(str(i)) for i in range(100)]
    game = Game(
        players=players,
        dealer_type=PerfectDealer,
        verbose=False
    )

    for i in range(N_ROUNDS):
        print('playing round', i)
        game.start_round()

    print('Average dealer win per round:', sum(game.collector.rewards['dealer']) / N_ROUNDS)
