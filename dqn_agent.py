import random
from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim

from rl_env import RLEnvironment


class EnemyDQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim),
        )

    def forward(self, x):
        return self.net(x)


class ReplayMemory:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, transition):
        self.buffer.append(transition)

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)


def train_dqn(
    episodes=1500,
    max_steps=400,
    gamma=0.99,
    lr=1e-3,
    batch_size=64,
    memory_capacity=50000,
    epsilon_start=1.0,
    epsilon_end=0.05,
    epsilon_decay=0.997,
    target_update_interval=10,
    model_path="enemy_dqn.pth",
):
    env = RLEnvironment(max_steps=max_steps)
    state = env.reset()
    state_dim = len(state)
    action_dim = 4
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    policy_net = EnemyDQN(state_dim, action_dim).to(device)
    target_net = EnemyDQN(state_dim, action_dim).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    optimizer = optim.Adam(policy_net.parameters(), lr=lr)
    memory = ReplayMemory(memory_capacity)
    epsilon = epsilon_start

    reward_history = []
    for episode in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0.0
        step_count = 0
        while not done and step_count < max_steps:
            step_count += 1
            if random.random() < epsilon:
                action = random.randint(0, action_dim - 1)
            else:
                with torch.no_grad():
                    s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
                    q_values = policy_net(s)
                    action = int(torch.argmax(q_values, dim=1).item())
            next_state, reward, done = env.step(action)
            total_reward += reward
            memory.push((state, action, reward, next_state, done))
            state = next_state

            if len(memory) >= batch_size:
                states, actions, rewards, next_states, dones = memory.sample(batch_size)
                states_tensor = torch.tensor(states, dtype=torch.float32, device=device)
                actions_tensor = torch.tensor(actions, dtype=torch.int64, device=device).unsqueeze(1)
                rewards_tensor = torch.tensor(rewards, dtype=torch.float32, device=device).unsqueeze(1)
                next_states_tensor = torch.tensor(next_states, dtype=torch.float32, device=device)
                dones_tensor = torch.tensor(dones, dtype=torch.bool, device=device).unsqueeze(1)

                q_values = policy_net(states_tensor).gather(1, actions_tensor)
                with torch.no_grad():
                    next_q_values = target_net(next_states_tensor).max(1, keepdim=True)[0]
                    target_q_values = rewards_tensor + gamma * next_q_values * (~dones_tensor)

                loss = nn.functional.mse_loss(q_values, target_q_values)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        reward_history.append(total_reward)
        if epsilon > epsilon_end:
            epsilon *= epsilon_decay
            if epsilon < epsilon_end:
                epsilon = epsilon_end

        if (episode + 1) % target_update_interval == 0:
            target_net.load_state_dict(policy_net.state_dict())
        if (episode + 1) % 50 == 0:
            recent = reward_history[-50:]
            avg_r = sum(recent) / len(recent)
            print(f"Episode {episode + 1}, avg reward {avg_r:.2f}, epsilon {epsilon:.3f}")

    torch.save(policy_net.state_dict(), model_path)


if __name__ == "__main__":
    train_dqn()
