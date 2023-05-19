import random

import torch
import numpy as np
import matplotlib as plot
from collections import deque
import game_ai as PokerGame
from model import Linear_QNet, QTrainer
import helper

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.01

GAME_NUM = 10

AI_PLAYER = 1

class Agent:

    def __init__(self):
        self.n_rounds = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet().to("cuda")
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cuda")
        print("Currently using {}".format(self.device))
        # Moves model to GPU

    @staticmethod
    def get_state(game): # [your card, turn number, current bet]
        if game.ai_player == 1:
            state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, game.turn, game.bet]
            state[game.p1_card] = 1
            return np.array(state, dtype=int)
        if game.ai_player == 2:
            state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, game.turn, game.bet]
            state[game.p2_card] = 1
            return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves:
        self.epsilon = 300 - self.n_rounds
        final_move = 0
        if random.randint(0,200) < self.epsilon:
            final_move = random.randint(0,1)
        else:
            state0 = torch.tensor(state,dtype=torch.float).to("cuda")
            bet_prob_list = self.model(state0).tolist()
            bet_prob_0 = bet_prob_list[0]
            bet_prob_1 = bet_prob_list[1]
            if bet_prob_1 > random.random() * (bet_prob_0 + bet_prob_1):
                final_move = 1
            else:
                final_move = 0
        return final_move


def train():
    # plot_scores = []
    plot_mean_scores = []
    past_hundred_mean_scores = []
    past_hundred_scores = []
    past_hundred_total = 0
    total_score = 0
    record = 0
    agent = Agent()
    game = PokerGame.Game(AI_PLAYER)
    saved = False
    while True:

        game_count = 0
        state_old = None
        final_move = None
        reward = None
        state_new = None
        done = False

        while game_count < GAME_NUM:
            if game.ai_player == 1 and game.get_player_turn() == 2:
                game.play_table_two()
            elif game.ai_player == 2 and game.get_player_turn() == 1:
                game.play_table_one()
            elif game.ai_player == game.get_player_turn():
                # get old state
                state_old = agent.get_state(game)

                # get move
                final_move = agent.get_action(state_old)

                # perform move and get new state
                reward = game.play_step(final_move)
                state_new = agent.get_state(game)
                done = False

                # train short memory
                agent.train_short_memory(state_old, final_move, reward, state_new, done)

                # remember
                agent.remember(state_old, final_move, reward, state_new, done)
            if game.turn < 0:
                game.reset()
                game_count+=1

        coins = game.get_ai_coins()
        reward = coins * 1000
        game.reset_coins()
        agent.n_rounds += 1
        done = True
        agent.remember(state_old, final_move, reward, state_new, done)
        agent.train_long_memory()
        if coins > record:
            record = coins
            # agent.model.save()
        # print('Round {}, Coins: {}, Record: {}'.format(agent.n_rounds, coins, record))

        # plot_scores.append(coins)
        total_score += coins
        if len(past_hundred_scores) < 100:
            past_hundred_scores.append(coins)
            past_hundred_total += coins
            past_hundred_mean_scores.append(past_hundred_total / len(past_hundred_scores))
        else:
            past_hundred_scores.append(coins)
            past_hundred_total += coins
            past_hundred_total -= past_hundred_scores.pop(0)
            past_hundred_mean_scores.append(past_hundred_total / 100)


        mean_score = total_score / agent.n_rounds
        if past_hundred_total > -100 and agent.n_rounds > 200 and not saved:
            agent.model.save()
            saved = True
        plot_mean_scores.append(mean_score)
        helper.plot(past_hundred_mean_scores, plot_mean_scores)



if __name__ == "__main__":
    train()