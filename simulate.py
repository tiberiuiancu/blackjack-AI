from blackjack.game import Game
from blackjack.player import *
from blackjack.dealer import *
import numpy as np

# np.random.seed(0)

if __name__ == '__main__':
    game = Game(
        (HumanPlayer('P1'),
         HumanPlayer('P2')),
        dealer_type=PerfectDealer
    )

    game.start_round()
