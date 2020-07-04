from blackjack.game import Game
from blackjack.player import *
from blackjack.dealer import *
import numpy as np
import matplotlib.pyplot as plt
import pickle
import time


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


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


LOAD = True
TRAINING_ROUNDS = 0 * 500 * 1000
VALIDATION_ROUNDS = 50
PRINT_EVERY = 100
SAVE_EVERY = 1000
VALIDATE_EVERY = TRAINING_ROUNDS // 100
N_PLAYERS = 5

if __name__ == '__main__':
    players = [QPlayer(str(i)) for i in range(N_PLAYERS)]

    if LOAD:
        for player in players:
            with open('savefile' + player.name + '.pickle', 'rb') as f:
                player.qvalues = pickle.load(f)

        try:
            with open('validation.pickle', 'rb') as f:
                validation = pickle.load(f)
        except FileNotFoundError:
            validation = []

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

    for player in players:
        player.training = False

    game = Game(
        players=players,
        dealer_type=PerfectDealer,
        verbose=False,
        collect_stats=True
    )

    for i in range(100):
        print(i)
        game.start_round()

    cumulative_rewards = {}
    for i in range(N_PLAYERS):
        name = str(i)
        cumulative_rewards[name] = [0]
        for j, reward in enumerate(game.collector.rewards[name]):
            cumulative_rewards[name].append(cumulative_rewards[name][j] + reward)

    name = 'dealer'
    cumulative_rewards[name] = [0]
    for j, reward in enumerate(game.collector.rewards[name]):
        cumulative_rewards[name].append(cumulative_rewards[name][j] + reward)

    for i in range(N_PLAYERS):
        plt.plot(cumulative_rewards[str(i)])
    plt.plot(cumulative_rewards['dealer'], label='dealer')
    plt.show()
