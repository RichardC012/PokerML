import random

PLAYER_TABLE_1 = [[0.454, 0.443, 0.254, 0.000, 0.000, 0.000, 0.000, 0.422, 0.549, 0.598, 0.615, 0.628, 0.641],
                  [0.000, 0.000, 0.169, 0.269, 0.429, 0.610, 0.760, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]]

PLAYER_TABLE_2 = [[1.000, 1.000, 0.000, 0.000, 0.000, 0.000, 0.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000],
                  [0.000, 0.000, 0.000, 0.251, 0.408, 0.583, 0.759, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]]

CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

class Game:

    def __init__(self, player):
        self.p1_coins = 0
        self.p2_coins = 0
        self.p1_card = -1
        self.p2_card = -1
        self.turn = 0 # 0, 1, or 2 [Player turn: self.turn % 2 + 1]
        self.bet = 0
        self.pot = 0
        self.ai_player = player # 1 or 2

    def reset(self):
        self.p1_card = random.randrange(13)
        self.p2_card = random.randrange(13)
        self.player_print("Player 1 has {}, Player 2 has {}".format(CARDS[self.p1_card], CARDS[self.p2_card]))
        self.turn = 0  # 0, 1, 2, -1, -2, -3 // -1 means player 1 wins, -2 means player 2 wins, -3 means showdown
        self.bet = 0
        self.p1_coins -= 1
        self.p2_coins -= 1
        self.pot = 2

    def reset_coins(self):
        self.p1_coins = 0
        self.p2_coins = 0
        self.reset()

    def play_step(self, move): # returns Reward
        if self.ai_player == 1:
            self.play_move_one(move)
        elif self.ai_player == 2:
            self.play_move_two(move)
        if self.turn < 0:
            return self.showdown()
        else:
            return 0



    def play_move_one(self, move): # move is 1 or 0 for the bet
        if self.turn == 0:
            self.p1_coins -= move
            self.bet = move
            self.pot += move
            self.turn = 1
            if move:
                self.player_print("Player 1 bets 1 coin.")
            else:
                self.player_print("Player 1 bets 0 coins.")
        elif self.turn == 2:
            if move == 0:
                self.turn = -2
                self.player_print("Player 1 bets 0 coins -- Folds")
            if move == 1:
                self.p1_coins -= 1
                self.pot += 1
                self.turn = -3
                self.player_print("Player 1 bets 1 coin -- Entering Showdown")
        else:
            raise Exception("Player One played a move when it was not their turn")

    def play_move_two(self, move):
        if self.turn == 1:
            if self.bet == 0 and move == 0:
                self.turn = -3
                self.player_print("Player 2 bets 0 coins -- Entering Showdown")
            elif self.bet == 0 and move == 1:
                self.p2_coins -= 1
                self.bet = 1
                self.pot += 1
                self.turn = 2
                self.player_print("Player 2 bets 1 coin.")
            elif self.bet == 1 and move == 0:
                self.turn = -1
                self.player_print("Player 2 bets 0 coins -- Folds")
            elif self.bet == 1 and move == 1:
                self.p2_coins -= 1
                self.pot += 1
                self.turn = -3
                self.player_print("Player 2 bets 1 coin -- Entering Showdown")
        else:
            raise Exception("Player Two played a move when it was not their turn")


    def showdown(self): # turn should be -1, -2, or -3, RETURNS: reward based on win/loss
        reward_one = 0
        reward_two = 0
        if self.turn == -1:
            self.p1_coins += self.pot
            self.player_print("Player 1 wins {} coins.".format(self.pot))
            reward_one = self.pot
            reward_two = -self.pot
        if self.turn == -2:
            self.p2_coins += self.pot
            self.player_print("Player 2 wins {} coins.".format(self.pot))
            reward_one = -self.pot
            reward_two = self.pot
        if self.turn == -3:
            self.player_print("Player 1 is holding a {}. Player 2 is holding a {}.".format(CARDS[self.p1_card], CARDS[self.p2_card]))
            if self.p1_card > self.p2_card:
                self.p1_coins += self.pot
                self.player_print("Player 1 has the higher card and wins {} coins.".format(self.pot))
                reward_one = self.pot
                reward_two = -self.pot
            elif self.p1_card < self.p2_card:
                self.p2_coins += self.pot
                self.player_print("Player 2 has the higher card and wins {} coins.".format(self.pot))
                reward_one = -self.pot
                reward_two = self.pot
            elif self.p1_card == self.p2_card:
                self.p1_coins += int(self.pot / 2)
                self.p2_coins += int(self.pot / 2)
                self.player_print("Both players have the same cards, the pot is split.")
                reward_one = int(self.pot / 2)
                reward_two = int(self.pot / 2)
        self.pot = 0
        if self.ai_player == 1:
            if reward_one > 0:
                return 1
            else:
                return -1
        elif self.ai_player == 2:
            if reward_two < 0:
                return reward_two
            else:
                return reward_two


    def play_table_one(self): # returns bet value of 0 or 1
        bet_prob = PLAYER_TABLE_1[int(self.turn/2)][self.p1_card]
        if bet_prob > random.random():
            self.play_move_one(1)
        else:
            self.play_move_one(0)
        if self.turn < 0:
            self.showdown()

    def play_table_two(self):
        bet_prob = PLAYER_TABLE_2[self.bet][self.p2_card]
        if bet_prob > random.random():
            self.play_move_two(1)
        else:
            self.play_move_two(0)
        if self.turn < 0:
            self.showdown()

    def get_player_turn(self):
        return self.turn % 2 + 1

    def get_ai_coins(self):
        if self.ai_player == 1:
            return self.p1_coins
        elif self.ai_player == 2:
            return self.p2_coins

    def player_print(self, string):
        if self.ai_player == 0:
            print(string)
