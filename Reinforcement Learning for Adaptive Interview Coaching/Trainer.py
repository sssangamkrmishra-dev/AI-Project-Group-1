from QLearningAgent import QLearningAgent, ACTIONS
from Student import StudentEnv
import pickle

env = StudentEnv()
agent = QLearningAgent(ACTIONS)

episodes = 5000
for ep in range(episodes):
    state = env.reset()
    done = False
    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.learn(state, action, reward, next_state, done)
        state = next_state
    agent.decay_epsilon()

with open("model/q_table.pkl", "wb") as f:
    pickle.dump(dict(agent.q_table), f)  
