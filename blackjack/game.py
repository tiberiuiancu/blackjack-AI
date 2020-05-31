from .deck import Deck
from .dealer import RandomDealer
from .utils import busted, blackjack, get_hand_value
from copy import deepcopy as cp

N_DECKS = 5

# game phases
PLAYERS_TURN = 0
DEALERS_TURN = 1
GAME_OVER = 2


class Game:
    def __init__(self, players=(), dealer_type=RandomDealer):
        self.deck = Deck(N_DECKS)
        self.players = []
        self.dealer = dealer_type()
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
            player.give_card(self.deck.draw_card())

        # do the same for the dealer
        self.dealer.reset_cards()
        self.dealer.give_card(self.deck.draw_card())
        self.dealer.give_card(self.deck.draw_card())

        while self.phase == PLAYERS_TURN:
            # assume all players have no moves until proven otherwise
            self.phase = DEALERS_TURN

            for player in self.players:
                if player.can_make_move():
                    # if we can still make moves we remain in the players turn phase
                    self.phase = PLAYERS_TURN

                    # perform the move for the current player if they dont have a blackjack
                    if not player.has_blackjack():
                        self.do_move(player, player.make_move(deck=cp(self.deck)))
                    else:
                        # move to the next hand
                        player.current_hand += 1

        # now we have to make the move for the dealer
        last_dealer_move = ''
        while last_dealer_move != 'stand' and not self.dealer.busted():
            last_dealer_move = self.dealer.make_move(self.players)
            if last_dealer_move == 'hit':
                self.dealer.give_card(self.deck.draw_card())

        # end of game; compute outcome
        player_rewards = []
        dealer_reward = 0
        for player in self.players:
            player_reward = 0
            for cards, bet in zip(player.cards, player.bets):
                if busted(cards) or get_hand_value(cards) < get_hand_value(self.dealer.cards):
                    # if busted or lost, you don't get anything, but the dealer get your bet
                    dealer_reward += bet
                elif blackjack(cards) and not blackjack(self.dealer.cards):
                    # if blackjack, you get the bet back and 1.5 * bet more
                    player_reward += 2.5 * bet
                    # dealer gets your bet but loses 2.5 * bet
                    dealer_reward -= 1.5 * bet
                elif get_hand_value(cards) > get_hand_value(self.dealer.cards):
                    # if you have value higher than dealer, you get your bet back and 1 * bet more
                    player_reward += 2 * bet
                    # dealer gets your bet but loses 2 * bet
                    dealer_reward -= bet
                elif get_hand_value(cards) == get_hand_value(self.dealer.cards):
                    # if it's a tie, you get your bet back
                    player_reward += bet

            player_rewards.append(player_reward)

        for reward in player_rewards:
            print(reward)

        print('DEALER: ', dealer_reward)

    def do_move(self, player, move):
        move = move.lower()
        if move == 'hit':
            player.give_card(self.deck.draw_card())
            if player.busted():
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
