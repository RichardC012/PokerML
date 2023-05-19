import random

PLAYER_TABLE_1 = [[0.454, 0.443, 0.254, 0.000, 0.000, 0.000, 0.000, 0.422, 0.549, 0.598, 0.615, 0.628, 0.641],
                  [0.000, 0.000, 0.169, 0.269, 0.429, 0.610, 0.760, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]]

PLAYER_TABLE_2 = [[1.000, 1.000, 0.000, 0.000, 0.000, 0.000, 0.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000],
                  [0.000, 0.000, 0.000, 0.251, 0.408, 0.583, 0.759, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]]

CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

REPS = 100000



class Game:

    def __init__(self, player):
        self.p1_coins = 0
        self.p2_coins = 0
        self.p1_card = -1
        self.p2_card = -1
        self.turn = 0 # 0, 1, or 2
        self.bet = 0
        self.pot = 0
        self.player = player # 1 or 2 or 0


    def start(self):
        if self.player == 1 or self.player == 2:
            while True:
                self.p1_card = random.randrange(13)
                self.p2_card = random.randrange(13)
                self.turn = 0 # 0, 1, 2, -1, -2, -3 // -1 means player 1 wins, -2 means player 2 wins, -3 means showdown
                self.bet = 0
                self.p1_coins -= 1
                self.p2_coins -= 1
                self.pot = 2
                print("You are Player {}".format(self.player))
                if self.player == 1:
                    print("You are holding: {}".format(CARDS[self.p1_card]))
                elif self.player == 2:
                    print("You are holding: {}".format(CARDS[self.p2_card]))
                while self.turn >= 0:
                    self.play_turn()
                self.showdown(self.turn)
                print("Player 1 has {} coins. Player 2 has {} coins.".format(self.p1_coins, self.p2_coins))
                continue_input = ""
                while continue_input != "c" or self.player == 0:
                    continue_input = input("To continue, press 'c'\n")
        elif self.player == 0:
            reps = REPS
            while reps > 0:
                self.p1_card = random.randrange(13)
                self.p2_card = random.randrange(13)
                self.turn = 0  # 0, 1, 2, -1, -2, -3 // -1 means player 1 wins, -2 means player 2 wins, -3 means showdown
                self.bet = 0
                self.p1_coins -= 1
                self.p2_coins -= 1
                self.pot = 2
                while self.turn >= 0:
                    self.play_turn()
                self.showdown(self.turn)
                print("Rep: {} Player 1 has {} coins, Player 2 has {} coins".format(reps, self.p1_coins, self.p2_coins))
                reps -= 1
            print("After {} reps, Player 1 has {} coins. Player 2 has {} coins.".format(REPS, self.p1_coins, self.p2_coins))

    def play_turn(self):
        move = self.get_bet(self.turn % 2 + 1)
        self.play_move(move)

    def play_move(self, move): # move is True or False for 1 bet and 0 bet
        if self.turn == 0:
            self.p1_coins -= move
            self.bet = move
            self.pot += move
            self.turn = 1
            if move:
                self.player_print("Player 1 bets 1 coin.")
            else:
                self.player_print("Player 1 bets 0 coins.")
        elif self.turn == 1:
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
        elif self.turn == 2:
            if move == 0:
                self.turn = -2
                self.player_print("Player 1 bets 0 coins -- Folds")
            if move == 1:
                self.p1_coins -= 1
                self.pot += 1
                self.turn = -3
                self.player_print("Player 1 bets 1 coin -- Entering Showdown")

    def showdown(self, turn): # turn should be -1, -2, or -3
        if turn == -1:
            self.p1_coins += self.pot
            self.player_print("Player 1 wins {} coins.".format(self.pot))
        if turn == -2:
            self.p2_coins += self.pot
            self.player_print("Player 1 wins {} coins.".format(self.pot))
        if turn == -3:
            self.player_print("Player 1 is holding a {}. Player 2 is holding a {}.".format(CARDS[self.p1_card], CARDS[self.p2_card]))
            if self.p1_card > self.p2_card:
                self.p1_coins += self.pot
                self.player_print("Player 1 has the higher card and wins {} coins.".format(self.pot))
            elif self.p1_card < self.p2_card:
                self.p2_coins += self.pot
                self.player_print("Player 2 has the higher card and wins {} coins.".format(self.pot))
            elif self.p1_card == self.p2_card:
                self.p1_coins += int(self.pot / 2)
                self.p2_coins += int(self.pot / 2)
                self.player_print("Both players have the same cards, the pot is split.")
        self.pot = 0


    def get_bet(self, player): # returns bet value of 0 or 1
        if player != self.player or self.player == 0:
            if player == 1:
                bet_prob = PLAYER_TABLE_1[int(self.turn/2)][self.p1_card]
                if bet_prob > random.random():
                    return 1
                else:
                    return 0
            elif player == 2:
                bet_prob = PLAYER_TABLE_2[self.bet][self.p2_card]
                if bet_prob > random.random():
                    return 1
                else:
                    return 0
        elif player == self.player:
            player_input = ""
            while player_input != "0" and player_input != "1":
                player_input = input("Type '0' to bet 0 coins, or '1' to bet a coin.\n"
                                     "Betting 0 coins when the opponent has bet a coin is considered a fold.\n")
            return int(player_input)

    def player_print(self, string):
        if self.player == 1 or self.player == 2:
            print(string)


if __name__ == '__main__':
    start_input = ""
    while start_input != "1" and start_input != "2" and start_input != "0":
        start_input = input("Type '1' or '2' for Player 1 or Player 2\n")
    game = Game(int(start_input))
    game.start()