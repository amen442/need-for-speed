import gymnasium
from gymnasium import spaces
import numpy as np
import random

class CarGameEnv(gymnasium.Env):
    def __init__(self):
        super(CarGameEnv, self).__init__()
        self.lanes = [150, 250, 350]
        self.action_space = spaces.Discrete(3)  # 0: stay, 1: left, 2: right
        self.observation_space = spaces.Box(low=np.array([-100]*8), high=np.array([600]*8), dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.player_x = 250
        self.player_y = 400
        self.vehicles = []
        self.score = 0
        self.done = False
        self.speed = 10
        obs = self._get_obs()
        return obs, {}

    def _get_obs(self):
        obs = [self.player_x, self.player_y]
        vehicles_sorted = sorted(self.vehicles, key=lambda v: v["y"])[:3]
        for v in vehicles_sorted:
            obs.append(v["x"])
            obs.append(v["y"])
        while len(obs) < 8:
            obs += [0, 0]
        return np.array(obs, dtype=np.float32)

    def step(self, action):
        if self.done:
            return self._get_obs(), 0, True, False, {}

        if action == 1 and self.player_x > 150:
            self.player_x -= 100
        elif action == 2 and self.player_x < 350:
            self.player_x += 100

        for v in self.vehicles:
            v["y"] += self.speed
        self.vehicles = [v for v in self.vehicles if v["y"] < 500]

        if len(self.vehicles) < 3:
            self.vehicles.append({
                "x": random.choice(self.lanes),
                "y": -50
            })

        for v in self.vehicles:
            if abs(self.player_x - v["x"]) < 50 and abs(self.player_y - v["y"]) < 50:
                self.done = True
                return self._get_obs(), -10, True, False, {}

        self.score += 1
        reward = 0.1
        return self._get_obs(), reward, False, False, {}

    def render(self):
        pass
