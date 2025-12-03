import pickle
from Student import StudentEnv
from QLearningAgent import QLearningAgent, ACTIONS

if __name__ == "__main__":
    env = StudentEnv()
    agent = QLearningAgent(ACTIONS)
    with open("model/q_table.pkl", "rb") as f:
        agent.q_table = pickle.load(f)
    agent.epsilon = 0.0 

    print("AI Coach ready!")

    conf = int(input("Confidence (0-20): "))
    mastery = int(input("Mastery (0-20): "))
    burnout = float(input("Burnout (0.0-1.0): "))

    state = env.reset((conf, burnout, mastery, 30))

    print("\nDay | Action | Conf | Mastery | Burnout")
    print("-"*40)

    done = False
    while not done:
        action_idx = agent.choose_action(state, training=False)
        action_name = ACTIONS[action_idx]
        next_state, reward, done = env.step(action_idx)
        print(f"{30 - env.timeleft:<3} | {action_name:<20} | {env.conf:<4} | {env.mastery:<7} | {env.burnout:.2f}")
        state = next_state
        if env.mastery >= 20 and env.conf >= 20:
            print("\nStudent reached maximum mastery and confidence!")
            break
        if env.burnout== 1.0 :
            print("\nStudent reached maximum burnout tolerance!")
            break
