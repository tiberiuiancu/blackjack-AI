from blackjack.game import Game
from blackjack.player import RandomPlayer

if __name__ == '__main__':
    game = Game(
        (RandomPlayer(),
         RandomPlayer(),
         RandomPlayer(),
         RandomPlayer())
    )

    # simulate 1000 games
    for _ in range(1000):
        game.start_round()
