import random

import gym
import numpy as np
import sys

import gym_remote.exceptions as gre
import gym_remote.client as grc


# Parameters
EXPLOIT_BIAS = .25

right_steps = 100
left_steps = 70

jump_repeat = 4
jump_prob = .1

DO_RENDER = False
LOG_LEVEL = -1

def log(level, *args):
  global LOG_LEVEL
  if level <= LOG_LEVEL:
    print(*args)

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

# Assume the inputs are
#   game = argv[0]
#   state = argv[1]
#   max_timesteps = argv[2]
def main(argv = sys.argv[1:]):
  global EXPLOIT_BIAS

  # Assumed inputs are as follows
  game = argv[0]
  state = argv[1]
  max_timesteps = int(argv[2])

  env = grc.RemoteEnv('tmp/sock')
  env = TrackedEnv(env, max_timesteps)
  sequences = []
  while env.total_steps_ever < env.max_timesteps:
    env.reset()
    if do_exploit(env):
      exploit(env, sequences)
    else:
      explore(env, sequences)

  log(0, "finished simulation with mean score of {}".format(np.mean([reward for sequence in sequences for reward in sequence.rewards])))

def do_exploit(env):
  global EXPLOIT_BIAS
  if env.total_steps_ever == 0:
    return False

  exploit_prob = EXPLOIT_BIAS + (env.total_steps_ever / env.max_timesteps)
  log(1, "Flipped explot coin, EXPLOIT_BIAS = {}    exploit_prob = {}".format(EXPLOIT_BIAS, exploit_prob))
  return random.random() < exploit_prob



### Exploit ###
def exploit(env, sequences):
  best_sequence = get_best_sequence(sequences)
  log(1, "Exploiting sequence with mean reward {}".format(best_sequence.mean_reward()))
  done = perform_actions(env, sequences, best_sequence.actions)
  if done:
    log(1, "Ended exploited sequence with total reward {}".format(env.total_reward))
    best_sequence.rewards.append(env.total_reward)
  else:
    log(1, "Ran out of actions, exploring end of exploited sequence")
    explore(env, sequences)
    log(1, "Explored end of an exploited sequence with total reward {}".format(env.total_reward))

# Room for improvement. Think confidence intervals
def get_best_sequence(sequences):
  return max(sequences, key=lambda x: x.mean_reward())

def perform_actions(env, sequences, actions):
  done = False
  for action in actions:
    if done:
      break
    _, _, done, _ = env.step(action)

  return done



### Explore ###
def explore(env, sequences):
  log(1, "Exploring a new vein in the action space")
  global right_steps
  global left_steps

  done = False
  while not done:
    log(2, "moving right {} steps".format(right_steps))
    reward, done = move(env, 'right', right_steps)
    if not done and reward <= 0:
      log(2, "Moving left {} steps because a negative reward was detective".format(left_steps))
      _, done = move(env, 'left', left_steps)
  log(1, "Finished exploration with a total reward of {}".format(env.total_reward))
  sequences.append(env.history.best_sequence())

def move(env, movement, steps=0):
  total_reward = 0

  jump_steps = 0
  for step in range(steps):
    action, jump_steps = make_action(movement, jump_steps)

    _, reward, done, _ = env.step(action)
    total_reward += reward
    if done:
      break

  return total_reward, done


def make_action(movement, jump_steps):
  global jump_repeat
  global jump_prob

  action = np.zeros((12,), dtype=np.bool)
  # Designate direction
  if movement == 'left':
    action[6] = True
  elif movement == 'right':
    action[7] = True

  # Choose whether to jump
  if jump_steps <= 0:
    if random.random() < jump_prob:
      jump_steps = jump_repeat
  else:
      action[0] = True
      jump_steps -= 1

  return action, jump_steps





class TrackedEnv(gym.Wrapper):
  def __init__(self, env, max_timesteps):
    super(TrackedEnv, self).__init__(env)
    self.history = History()
    self.total_reward = 0
    self.total_steps_ever = 0
    self.max_timesteps = max_timesteps

    self.wait = True

  def reset(self, **kwargs):
    self.history = History()
    self.total_reward = 0
    self.wait = True
    return self.env.reset(**kwargs)

  def render(self):
    self.env.render()
    if (self.wait):
      cmd = input()
      if cmd == "s":
        self.wait = False

  def step(self, action):
    self.total_steps_ever += 1
    if self.total_steps_ever % 1000 == 0:
      log(0, "total_steps_ever = {}".format(self.total_steps_ever))
    obs, reward, done, info = self.env.step(action)

    global DO_RENDER
    if DO_RENDER:
      self.render()

    self.total_reward += reward
    self.history.append(action, self.total_reward)
    return obs, reward, done, info

if __name__ == '__main__':
  try:
    main()
  except gre.GymRemoteError as e:
    print('exception', e)
