import gym
import sys
from time import time
import numpy as np

# Add some more useful information and tracking to the environment
# object. Use this as a basis for other wrappers.
class BasicEnv(gym.Wrapper):
  def __init__(self, env, max_timesteps, do_render, monitor_path):
    super().__init__(env)
    self.episode_reward = 0
    self.episode_timesteps = 0
    self.trial_reward = 0
    self.trial_timesteps = 0
    self.num_episodes = 0
    self.max_timesteps = max_timesteps
    self.do_pause = do_render
    self.do_render = do_render
    if monitor_path:
      self.monitor = open(monitor_path,'w')
      self.monitor.write('r,l,t\n')
      self.episode_startt = time()
    else:
      self.monitor = None

  def reset(self, **kwargs):
    self.episode_reward = 0
    self.episode_timesteps = 0
    return self.env.reset(**kwargs)

  def step(self, action):
    obs, reward, done, info = self.env.step(action)

    self.episode_timesteps += 1
    self.trial_timesteps += 1


    self.episode_reward += reward
    self.trial_reward += reward

    if done:
      self.num_episodes += 1
      if self.monitor:
        self.monitor.write('{},{},{}\n'.format(self.episode_reward,
                                               self.episode_timesteps,
                                               time()-self.episode_startt))


    if self.trial_timesteps > self.max_timesteps:
      if self.monitor:
        self.monitor.close()
      sys.exit(0)

    if self.do_render:
      self.env.render()

    if self.do_pause:
      self.handle_input()

    return obs, reward, done, info

  def handle_input(self):
    cmd = input()
    if cmd == "s":
      self.do_pause = False


# Sequence: a tuple (Actions, Rewards) where Rewards is a list of
# rewards observed after executing the sequence of behaviors in
# Actions
class Sequence:
  def __init__(self, actions=[], rewards=[]):
    self.actions = actions.copy()
    self.rewards = rewards.copy()

  def mean_reward(self):
    return np.mean(self.rewards)


# History: a tuple (Actions, Rewards) where each element
# actions[i] corresponds to a **cumulative** reward at rewards[i]
class History:
  def __init__(self):
    self.actions = []
    self.rewards = []

  def append(self, action, reward):
    self.actions.append(action.copy())
    self.rewards.append(reward)

  def best_sequence(self):
    max_i = np.argmax(self.rewards)
    return Sequence(self.actions[:max_i+1], [self.rewards[max_i]])


# An environment wrapper that tracks the actions taken and their
# resulting rewards
class HistoriedEnv(BasicEnv):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.history = History()

  def reset(self, **kwargs):
    self.history = History()
    return super().reset(**kwargs)

  def step(self, action):
    obs, reward, done, info = super().step(action)
    self.history.append(action, self.episode_reward)
    return obs, reward, done, info
