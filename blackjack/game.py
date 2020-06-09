from .deck import Deck
from .dealer import RandomDealer
from .stats import Collector
from .utils import *
from .player import QPlayer
from copy import deepcopy as cp

N_DECKS = 5

# game phases
PLAYERS_TURN = 0
DEALERS_TURN = 1
GAME_OVER = 2


class Game:
    def __init__(self, players=(), dealer_type=RandomDealer, verbose=True, collect_stats=True):
        self.deck = Deck(N_DECKS)
        self.players = []
        self.dealer = dealer_type()
        self.add_players(players)
        self.phase = PLAYERS_TURN
        self.verbose = verbose
        self.collector = Collector() if collect_stats else None

    def add_players(self, players):
        for player in players:
            self.players.append(player)

    def start_round(self):
        if self.verbose:
            print('STARTING ROUND')

        # set game pahse
        self.phase = PLAYERS_TURN

        # for each player, reset their hands and deal them new cards
        for player in self.players:
            player.reset_cards()
            if type(player) == QPlayer and player.training:
                # give the player some random cards during training
                player.cards = [get_random_cards()]
            else:
                card1, card2 = self.deck.draw_card(), self.deck.draw_card()
                player.give_card(card1)
                player.give_card(card2)

            if self.verbose:
                print('PLAYER ' + player.name + ' cards:', cards_to_str(player.cards[0]))

        # do the same for the dealer
        self.dealer.reset_cards()
        self.dealer.give_card(self.deck.draw_card())
        self.dealer.give_card(self.deck.draw_card())

        if self.verbose:
            print('DEALER CARDS: ' + cards_to_str((self.dealer.cards[0],)) + '?')

        while self.phase == PLAYERS_TURN:
            # assume all players have no moves until proven otherwise
            self.phase = DEALERS_TURN

            for player in self.players:
                if player.can_make_move():
                    # if we can still make moves we remain in the players turn phase
                    self.phase = PLAYERS_TURN

                    # perform the move for the current player if they dont have a blackjack
                    if not player.has_blackjack():
                        if self.verbose:
                            print('\nPLAYER ' + player.name + ' to move')
                            print('CARDS: ' + cards_to_str(player.cards[player.current_hand]))
                            print('VALID MOVES: ' + ', '.join(player.get_valid_moves()))

                        # we give the player a deck with one of the dealer's cards added back in
                        self.do_move(player, player.make_move(deck=self.deck.add_card(self.dealer.cards[0]),
                                                              dealer_card=self.dealer.cards[1]))
                    else:
                        # move to the next hand
                        player.current_hand += 1

        # now we have to make the move for the dealer
        if self.verbose:
            print('\nDEALER\'S TURN: ' + cards_to_str(self.dealer.cards))

        last_dealer_move = ''
        while last_dealer_move != 'stand' and not self.dealer.busted():
            last_dealer_move = self.dealer.make_move(players=self.players, deck=cp(self.deck))
            if self.verbose:
                print('MOVE: ' + last_dealer_move)
            if last_dealer_move == 'hit':
                card_to_give = self.deck.draw_card()
                self.dealer.give_card(card_to_give)

                if self.verbose:
                    print('HIT ' + cards_to_str((card_to_give,)))
            elif self.verbose:
                print('STAND')

        # end of game; compute outcome
        player_rewards = []
        dealer_reward = 0
        for player in self.players:
            player_reward = 0
            for cards, bet in zip(player.cards, player.bets):
                comparison_value = compare_card_values(cards, self.dealer.cards)
                if not cards:
                    # if player surrendered
                    player_reward -= bet / 2
                    dealer_reward += bet / 2
                if busted(cards):
                    # if player busted
                    player_reward -= bet
                    dealer_reward += bet
                elif busted(self.dealer.cards):
                    # if dealer busted
                    player_reward += bet
                    dealer_reward -= bet
                elif blackjack(cards) and not blackjack(self.dealer.cards):
                    # if blackjack, you get 1.5 * bet
                    player_reward += 1.5 * bet
                    dealer_reward -= 1.5 * bet
                elif comparison_value > 0:
                    # if you have value higher than dealer, you get your bet back and 1 * bet more
                    player_reward += bet
                    dealer_reward -= bet
                elif comparison_value < 0:
                    # if you have value lower than dealer, you lose your bet
                    player_reward -= bet
                    dealer_reward += bet
                elif comparison_value == 0:
                    # if it's a tie, nothing happens
                    pass

            # collect stats
            if self.collector:
                self.collector.add_reward(player.name, player_reward)

            # collect info for verbose
            player_rewards.append(player_reward)

            # update the qvalues if necessary
            if type(player) == QPlayer and player.training:
                player.update_q(player_reward)

        if self.verbose:
            for reward, player in zip(player_rewards, self.players):
                print(player.name + ':', reward)

        # collect stats
        if self.collector:
            self.collector.add_reward('dealer', dealer_reward)

        if self.verbose:
            print('DEALER: ', dealer_reward)

    def do_move(self, player, move):
        move = move.lower()
        # add move to stats
        if self.collector:
            self.collector.add_move(player.name, player.cards[player.current_hand], move)
        if move == 'hit':
            card_to_give = self.deck.draw_card()
            player.give_card(card_to_give)

            if self.verbose:
                print('HIT ' + cards_to_str((card_to_give,)))

            if player.busted():
                if self.verbose:
                    print('BUSTED')

                player.current_hand += 1
        elif move == 'stand':
            # just advance the current hand
            player.current_hand += 1

            if self.verbose:
                print('STAND')
        elif move == 'double':
            # double gives a new card and moves to the next hand (if any)
            player.bets[player.current_hand] *= 2
            card_to_give = self.deck.draw_card()
            player.give_card(card_to_give)

            # add doubling to the training set
            if type(player) == QPlayer and player.training and not player.busted():
                cards = player.cards[player.current_hand]
                player.made_moves = (get_hand_value(cards), has_ace(cards), self.dealer.cards[1])

            if self.verbose:
                print('DOUBLE ' + cards_to_str((card_to_give,)))
                if player.busted():
                    print('BUSTED')

            player.current_hand += 1
        elif move == 'split':
            card1, card2 = self.deck.draw_card(), self.deck.draw_card()
            player.split(card1, card2)

            if self.verbose:
                print('SPLIT ' +
                      cards_to_str(player.cards[player.current_hand]) + '| ' +
                      cards_to_str(player.cards[player.current_hand + 1]))
        elif move == 'surrender':
            # we will clear the cards so we know later that the player surrendered
            player.cards = [[]]

            if self.verbose:
                print('SURRENDER')
