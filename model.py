import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class Linear_QNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(15, 32).to("cuda")
        self.linear2 = nn.Linear(32, 32).to("cuda")
        self.linear3 = nn.Linear(32, 2).to("cuda")

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = F.sigmoid(self.linear3(x))
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        t_state = torch.tensor(state, dtype=torch.float).to("cuda")
        t_next_state = torch.tensor(next_state, dtype=torch.float).to("cuda")
        t_action = torch.tensor(action, dtype=torch.float).to("cuda")
        t_reward = torch.tensor(reward, dtype=torch.float).to("cuda")
        t_done = torch.tensor(done, dtype=torch.float).to("cuda")

        if len(t_state.shape) == 1:
            t_state = torch.unsqueeze(t_state, 0)
            t_next_state = torch.unsqueeze(t_next_state, 0)
            t_action = torch.unsqueeze(t_action, 0)
            t_reward = torch.unsqueeze(t_reward, 0)
            t_done = (t_done, )

        # 1: predicted Q values with current state
        prediction = self.model(t_state)

        # 2: reward + gamma * max(next_predicted Q) value

        target = prediction.clone()
        for idx in range(len(t_done)):
            Q_new = t_reward[idx]
            if not t_done[idx]:
                Q_new = t_reward[idx] + self.gamma * torch.max(self.model(t_next_state[idx]))

            target[idx][torch.argmax(t_action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, prediction)
        loss.backward()

        self.optimizer.step()
