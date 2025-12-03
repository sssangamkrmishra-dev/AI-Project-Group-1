import numpy as np

ACTIONS = {
    0: "INCREASE_DIFFICULTY",
    1: "SWITCH_TOPIC",
    2: "GIVE_ENCOURAGEMENT",
    3: "OFFER_QUICK_REVISION"
}

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.q_table = {}  
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.decay = epsilon_decay
        self.min_epsilon = min_epsilon

    def _ensure_state(self, state):
        """Initialize Q-values for unseen states."""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.actions))

    def choose_action(self, state, training=True):
        self._ensure_state(state)
        if training and np.random.rand() < self.epsilon:
            return np.random.randint(len(self.actions))
        return int(np.argmax(self.q_table[state]))

    def learn(self, state, action, reward, next_state, done):
        self._ensure_state(state)
        self._ensure_state(next_state)
        best_next = int(np.argmax(self.q_table[next_state]))
        td_target = reward + (0 if done else self.gamma * self.q_table[next_state][best_next])
        self.q_table[state][action] += self.alpha * (td_target - self.q_table[state][action])

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)
