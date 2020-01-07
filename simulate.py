from game import Game
from dealer import get_best_move

game = Game()
game.start_round(2)

while not game.game_over and game.to_play < game.n_players:
    print()
    print([game.human_readable_cards(x) for x in game.game_state])
    print(game.get_valid_moves())
    move = input()
    state = game.step(move)

    if game.game_over:
        print(state)

while not game.game_over:
    dealer_move = get_best_move(game, [1 for _ in range(game.n_players)])
    print(dealer_move)
    game.step(dealer_move)
    print([game.human_readable_cards(x) for x in game.game_state])

print(game.outcomes)
