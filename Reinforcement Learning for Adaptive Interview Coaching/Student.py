import random
import numpy as np

ACTIONS = {
    0: "INCREASE_DIFFICULTY",
    1: "SWITCH_TOPIC",
    2: "GIVE_ENCOURAGEMENT",
    3: "OFFER_QUICK_REVISION"
}

class StudentEnv:
    """
    Confidence & Mastery: 0-20
    Burnout: 0.0-1.0
    Timeleft: 30 days
    Improved reward shaping so agent learns to encourage when burnout is high.
    """

    def __init__(self):
        self.reset()

    def reset(self, specific_state=None):
        if specific_state:
            self.conf, self.burnout, self.mastery, self.timeleft = specific_state
        else:
            self.conf = random.randint(0, 20)
            self.mastery = random.randint(0, 20)
            self.burnout = round(random.uniform(0.0, 1.0), 2)
            self.timeleft = 30
        self._steps_used = 0
        return self._get_state()

    def _get_state(self):
        burn_disc = int(round(self.burnout * 20))  # 0..20
        return (self.conf, burn_disc, self.mastery, self.timeleft)

    def step(self, action: int):
        prev_mastery = self.mastery
        prev_conf = self.conf
        prev_burn = self.burnout

        if action == 0:  # INCREASE_DIFFICULTY
            success_prob = 0.4 + (self.mastery / 50.0)
            if random.random() < success_prob:
                self.mastery = min(20, self.mastery + 2)
                self.conf = min(20, self.conf + 2)
                self.burnout += 0.1
            else:
                self.conf = max(0, self.conf - 2)
                self.burnout += 0.15

        elif action == 1:  # SWITCH_TOPIC
            self.burnout = max(0.0, self.burnout - 0.2)
            self.conf = min(20, self.conf + 1)

        elif action == 2:  # GIVE_ENCOURAGEMENT
            self.burnout = max(0.0, self.burnout - 0.4)
            self.conf = min(20, self.conf + 3)

        elif action == 3:  # OFFER_QUICK_REVISION
            self.mastery = min(20, self.mastery + 1)
            self.burnout = max(0.0, self.burnout - 0.1)
        else:
            raise ValueError(f"Unknown action: {action}")


        self.timeleft -= 1
        self._steps_used += 1
        self.mastery = int(self.mastery)
        self.conf = int(np.clip(self.conf, 0, 20))
        self.burnout = float(round(np.clip(self.burnout, 0.0, 1.0), 2))

        reward = 0.0
        mastery_gain = self.mastery - prev_mastery
        conf_gain = self.conf - prev_conf
        burn_reduction = max(0.0, prev_burn - self.burnout)

        reward += 5.0 * mastery_gain          
        reward += 1.5 * conf_gain             
        reward += 25.0 * burn_reduction       

        if prev_burn > 0.7:
            if action == 2:
                reward += 50.0   
            else:
                reward -= 20.0   

        if self.burnout > 0.9:
            reward -= 30.0

        reward -= 0.05 * self._steps_used

        done = False
        if self.timeleft <= 0:
            done = True
            if self.mastery >= 16:
                reward += 50.0
            elif self.mastery < 10:
                reward -= 50.0

        if self.burnout >= 1.0:
            done = True
            reward -= 100.0

        reward = float(round(np.clip(reward, -1000.0, 1000.0), 2))

        return self._get_state(), reward, done
