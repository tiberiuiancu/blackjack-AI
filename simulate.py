from blackjack.game import Game
from blackjack.player import *
from blackjack.dealer import *
import numpy as np

np.random.seed(0)

N_ROUNDS = 1000

if __name__ == '__main__':
    players = [QPlayer(str(i)) for i in range(5)]
    game = Game(
        players=players,
        dealer_type=PerfectDealer,
        verbose=False
    )

    for i in range(N_ROUNDS):
        print('playing round', i)
        game.start_round()

    game.verbose = True
    for player in players:
        player.training = False

    game.start_round()
