from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from CarGameEnv import CarGameEnv

env = CarGameEnv()
check_env(env)

model = DQN("MlpPolicy", env, verbose=1, learning_rate=1e-3, buffer_size=50000, learning_starts=1000)
model.learn(total_timesteps=200_000)
model.save("drl_car_agent")
print("✅ Modèle sauvegardé : drl_car_agent.zip")
