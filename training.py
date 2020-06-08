from blackjack.game import Game
from blackjack.player import *
from blackjack.dealer import *
import numpy as np
import pickle
import time

np.random.seed(0)

TRAINING_ROUNDS = 1 * 1000
PRINT_EVERY = 100
LOAD = True

if __name__ == '__main__':
    players = [QPlayer(str(i)) for i in range(5)]

    if not LOAD:
        game = Game(
            players=players,
            dealer_type=PerfectDealer,
            verbose=False
        )

        start_time = time.time()
        for i in range(TRAINING_ROUNDS):
            if i % PRINT_EVERY == PRINT_EVERY - 1:
                remaining = int((time.time() - start_time) * TRAINING_ROUNDS / i)
                print('ETA:', '%02d:%02d:%02d' % (remaining // 3600,
                                                  (remaining % 3600) // 60,
                                                  remaining % 3600 % 60))
            game.start_round()

        # save to not lose progress
        for i, player in enumerate(players):
            with open('savefile' + str(i) + '.pickle', 'wb') as f:
                pickle.dump(player.qvalues, f)
    else:
        for player in players:
            with open('savefile' + player.name + '.pickle', 'rb') as f:
                player.qvalues = pickle.load(f)

    for player in players:
        player.training = False

    # play a round with these players
    game = Game(
        players=players[:-1] + [HumanPlayer('human')],
        dealer_type=PerfectDealer,
        verbose=True
    )

    game.start_round()
