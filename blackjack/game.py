from .deck import Deck
from copy import deepcopy as cp

N_DECKS = 5

# game phases
PLAYERS_TURN = 0
DEALERS_TURN = 1
GAME_OVER = 2


class Game:
    def __init__(self, players=()):
        self.deck = Deck(N_DECKS)
        self.players = []
        self.add_players(players)
        self.phase = PLAYERS_TURN

    def add_players(self, players):
        for player in players:
            self.players.append(player)

    def start_round(self):
        # set game pahse
        self.phase = PLAYERS_TURN

        # for each player, reset their hands and deal them new cards
        for player in self.players:
            player.reset_cards()
            player.give_card(self.deck.draw_card())

        while self.phase == PLAYERS_TURN:
            # assume all players have no moves until proven otherwise
            self.phase = DEALERS_TURN

            for player in self.players:
                if player.can_make_move():
                    # if we can still make moves we remain in the players turn phase
                    self.phase = PLAYERS_TURN

                    # perform the move for the current player
                    self.do_move(player, player.make_move(cp(self.deck)))

    def do_move(self, player, move):
        move = move.lower()
        if move == 'hit':
            player.give_card(self.deck.draw_card())
            if player.bust():
                player.current_hand += 1
        elif move == 'stand':
            # just advance the current hand
            player.current_hand += 1
        elif move == 'double':
            # double gives a new card and moves to the next hand (if any)
            player.bets[player.current_hand] *= 2
            player.give_card(self.deck.draw_card())
            player.current_hand += 1
        elif move == 'split':
            player.split(self.deck.draw_card(), self.deck.draw_card())
