from blackjack.game import Game
from blackjack.player import *
from blackjack.dealer import *
import numpy as np
import pickle
import time


def save_values(players):
    # save to not lose progress
    for i, player in enumerate(players):
        with open('savefile' + str(i) + '.pickle', 'wb') as f:
            pickle.dump(player.qvalues, f)


TRAINING_ROUNDS = 1 * 5000 * 1000
PRINT_EVERY = 100
SAVE_EVERY = 1000
LOAD = False

if __name__ == '__main__':
    players = [QPlayer(str(i)) for i in range(5)]

    if LOAD:
        for player in players:
            with open('savefile' + player.name + '.pickle', 'rb') as f:
                player.qvalues = pickle.load(f)

    game = Game(
        players=players,
        dealer_type=PerfectDealer,
        verbose=False
    )

    start_time = time.time()
    for i in range(TRAINING_ROUNDS):
        if i % SAVE_EVERY == SAVE_EVERY - 1:
            print('SAVING')
            save_values(players)

        if i % PRINT_EVERY == PRINT_EVERY - 1:
            remaining = int((time.time() - start_time) / i * (TRAINING_ROUNDS - i))
            print('ETA:', '%02d:%02d:%02d' % (remaining // 3600,
                                              (remaining % 3600) // 60,
                                              remaining % 3600 % 60))
        game.start_round()
