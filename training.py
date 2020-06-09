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


def validate(players, n_games):
    game = Game(
        players=players,
        dealer_type=PerfectDealer,
        verbose=False,
        collect_stats=True
    )

    # turn training off
    for player in players:
        player.training = False

    for _ in range(n_games):
        game.start_round()

    # turn training back on
    for player in players:
        player.training = True

    # average the dealer reward
    dealer_reward = sum(game.collector.rewards['dealer']) / n_games

    # average player rewards
    player_reward = 0
    for player in players:
        player_reward += sum(game.collector.rewards[player.name]) / n_games
    player_reward /= len(players)

    return player_reward, dealer_reward


TRAINING_ROUNDS = 1 * 5000 * 1000
VALIDATION_ROUNDS = 100
PRINT_EVERY = 100
SAVE_EVERY = 1000
VALIDATE_EVERY = TRAINING_ROUNDS // 1000
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
        verbose=False,
        collect_stats=False
    )

    # collect validation results here
    stats = []

    start_time = time.time()
    for i in range(TRAINING_ROUNDS):
        game.start_round()

        # validate
        if i % VALIDATE_EVERY == VALIDATE_EVERY - 1:
            print('VALIDATING...', end='', flush=True)
            stats.append(validate(players, VALIDATION_ROUNDS))
            print('PLAYER:', stats[-1][0], 'DEALER:', stats[-1][1])

            # also save stats
            with open('validation.pickle', 'wb') as f:
                pickle.dump(stats, f)

        # save
        if i % SAVE_EVERY == SAVE_EVERY - 1:
            print('SAVING')
            save_values(players)

        # print ETA
        if i % PRINT_EVERY == PRINT_EVERY - 1:
            remaining = int((time.time() - start_time) / i * (TRAINING_ROUNDS - i))
            print('ETA:', '%02d:%02d:%02d' % (remaining // 3600,
                                              (remaining % 3600) // 60,
                                              remaining % 3600 % 60))
