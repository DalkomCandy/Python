import keras as ks
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory
from tkinter import TclError

import t48_env


def init_network():
    # Keras initial model and layers
    model = ks.Sequential()
    model.add(ks.layers.Dense(16, input_shape=(1, 4, 4), activation="relu"))  # Hidden layer 1
    model.add(ks.layers.Dense(16, activation="relu"))  # Hidden layer 2
    model.add(ks.layers.Dense(1, activation="linear"))  # 1 list of 4 possible movements for output
    model.add(ks.layers.Flatten())

    print(model.summary())

    memory = SequentialMemory(limit=50000, window_length=1)
    policy = EpsGreedyQPolicy()  # THIS MIGHT BE WRONG
    agent = DQNAgent(model=model, nb_actions=4, memory=memory, nb_steps_warmup=100,
                     target_model_update=1e-2, policy=policy)
    agent.compile(ks.optimizers.Adam(lr=1e-3))
    return agent


def train_network(agent):
    env = t48_env.Twenty48Gym()
    agent.fit(env, nb_steps=float("inf"), visualize=True, nb_max_episode_steps=0)
    return env


dqn_agent = init_network()
try:
    gym_env = train_network(dqn_agent)
except (KeyboardInterrupt, TclError):
    dqn_agent.save_weights('dqn_t48_weights.h5f', overwrite=True)
    exit()
dqn_agent.save_weights('dqn_t48_weights.h5f', overwrite=True)
dqn_agent.test(gym_env, nb_episodes=5, visualize=True)
