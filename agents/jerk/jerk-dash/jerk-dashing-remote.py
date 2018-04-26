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

def set_dash(env):
  log(2, "Testing spin dash")
  reward_start = env.total_reward
  action = [False]*12
  done = False

  # Crouch down to prepare charge up
  for _ in range(10):
    if done:
      break
    action[5] = True
    _, reward, done, _ = env.step(action)

  # Charge up to prepare for dash
  action[0] = True
  for _ in range(10):
    if done:
      break;
    _, reward, done, _ = env.step(action)

  # Release buttons and do the dash
  if not done:
    action[0] = False
    action[5] = False
    _, reward, done, _ = env.step(action)

  global dash
  if reward > 0:
    log(2, "setting dash as spin_dash")
    dash = do_spin_dash
  else:
    log(2, "setting dash as running_dash")
    dash = do_running_dash

  print("dashing reward = {}".format(env.total_reward - reward_start))

  # Try to die quickly
  explore(env, [])
  env.reset()


# Assume the inputs are
#   game = argv[0]
#   state = argv[1]
#   max_timesteps = argv[2]
def main(argv = sys.argv[1:]):
  global EXPLOIT_BIAS

  # Assumed inputs are as follows
  max_timesteps = float('inf')

  env = grc.RemoteEnv('tmp/sock')
  env = TrackedEnv(env, max_timesteps)
  env.reset()

  set_dash(env)

  sequences = []
  explore(env, sequences)
  while env.total_steps_ever < env.max_timesteps:
    env.reset()
    if do_exploit(env):
      exploit(env, sequences)
    else:
      explore(env, sequences)

  log(0, "finished simulation with mean score of {}".format(np.mean([reward for sequence in sequences for reward in sequence.rewards])))


# Coin flip to decide whether to exploit or explore
def do_exploit(env):
  global EXPLOIT_BIAS

  exploit_prob = EXPLOIT_BIAS + (env.total_steps_ever / env.max_timesteps)
  log(1, "Flipped explot coin, EXPLOIT_BIAS = {}    exploit_prob = {}".format(EXPLOIT_BIAS, exploit_prob))
  return random.random() < exploit_prob


### Exploit ###
def exploit(env, sequences):
  best_sequence = get_best_sequence(sequences)
  log(1, "Exploiting sequence with mean reward {}".format(best_sequence.mean_reward()))
  done = perform_actions(env, sequences, best_sequence.actions)
  if not done:
    log(1, "Ran out of actions, inserting no-ops")
    env.wait = -float('inf')
    env.watch = False
    while not done:
      obs, rew, done, _ = env.step([0]*12)

  log(1, "Ended exploited sequence with total reward {}".format(env.total_reward))
  best_sequence.rewards.append(env.total_reward)


# Determine what the best sequence of actions so far has been
# Room for improvement. Think confidence intervals
def get_best_sequence(sequences):
  return max(sequences, key=lambda x: x.mean_reward())


# Perform all the actions of some sequence
def perform_actions(env, sequences, actions):
  for action in actions:
    _, _, done, _ = env.step(action)
    if done:
      break

  return done


### Explore ###
def explore(env, sequences):
  log(1, "Exploring a new vein in the action space")
  global right_steps
  global left_steps
  global dash

  done = False
  while not done:
    log(2, "moving right {} steps".format(right_steps))
    reward, done = move(env, 'right', right_steps)
    log(2, "right move reward of {}".format(reward))
    if not done and reward <= 0:
      log(2, "Negative reward detected. Attempting spin dash")
      reward, done = dash(env)
    if not done and reward <= 0:
      log(2, "Negative reward detected. Moving left {} steps".format(left_steps))
      _, done = move(env, 'left', left_steps)
  log(1, "Finished exploration with a total reward of {}".format(env.total_reward))
  sequences.append(env.history.best_sequence())

def do_running_dash(env):
  log(2, "performing running dash")
  reward_start = env.total_reward
  action = [False]*12
  done = False

  log(2, "  Backing up")
  # Back up a little bit
  global left_steps
  action[6] = True
  for _ in range(30):
    if done:
      break
    _, reward, done, _ = env.step(action)
  action[6] = False

  log(2, "  Sprinting right")
  # Sprint to the right, no jumps
  action[7] = True
  for _ in range(60):
    if done:
      break
    _, reward, done, _ = env.step(action)
  while reward > 0:
    if done:
      break
    _, reward, done, _ = env.step(action)
  action[7] = False

  return env.total_reward - reward_start, done

dash = do_running_dash

def do_spin_dash(env):
  log(2, "performing spin dash")
  reward_start = env.total_reward
  action = [False]*12
  done = False

  # Alternate back and forth
  action[6] = True
  for _ in range(10):
    if done:
      break
    _, reward, done, _ = env.step(action)
    action[6] = not action[6]
    action[7] = not action[7]
  action = [False]*12

  # Turn to the right
  action[7] = True
  for _ in range(7):
    if done:
      break
    _, reward, done, _ = env.step(action)
  action[7] = False

  # Stop Moving
  action = [False] * 12
  for _ in range(20):
    if done:
      break
    _, reward, done, _ = env.step(action)

  # Crouch down to prepare charge up
  for _ in range(10):
    if done:
      break
    action[5] = True
    _, reward, done, _ = env.step(action)

  # Charge up to prepare for dash
  action[0] = True
  for _ in range(20):
    if done:
      break;
    _, reward, done, _ = env.step(action)

  # Release buttons and do the dash
  if not done:
    action[0] = False
    action[5] = False
    _, reward, done, _ = env.step(action)

  # Let it go while it's good
  for _ in range(10):
    if done:
      break
    _, reward, done, _ = env.step(action)

  while reward > 0 and not done:
    _, reward, done, _ = env.step(action)

  return env.total_reward - reward_start, done

# Move Sonic to the right or the left with coin-flips for jumping
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


# Construct the actual action data structure
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
      log(2, 'chose to jump')
      jump_steps = jump_repeat
  else:
    action[0] = True
    jump_steps -= 1

  return action, jump_steps


# An environment wrapper that tracks the actions taken and their
# resulting rewards
class TrackedEnv(gym.Wrapper):
  def __init__(self, env, max_timesteps):
    global DO_RENDER
    super(TrackedEnv, self).__init__(env)
    self.history = History()
    self.total_reward = 0
    self.total_steps_ever = 0
    self.max_timesteps = max_timesteps
    self.watch = DO_RENDER
    self.wait = float('inf')

  def reset(self, **kwargs):
    global DO_RENDER
    self.history = History()
    self.total_reward = 0
    self.watch = DO_RENDER
    self.wait = float('inf') if DO_RENDER else -float('inf')
    return self.env.reset(**kwargs)

  # This controls the rendering process, allowing controls via stdin
  def render(self):
    self.wait += 1
    if self.watch:
      self.env.render()
    if self.wait > 0:
      cmd = input().split()
      if len(cmd) == 0:
        pass
      elif cmd[0] == "ff": # Fast forward
        if len(cmd) == 1:
          self.wait = -float("inf")
        else:
          self.wait = -int(cmd[1])+1
      elif cmd[0] == "skip": # Skip episode
        self.wait = -float('inf')
        self.watch = False


  def step(self, action):
    button_map = ['B', 'A', 'MODE', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT',
                  'C', 'Y', 'X', 'Z']
    self.total_steps_ever += 1
    if self.total_steps_ever % 1000 == 0:
      log(0, "total_steps_ever = {}".format(self.total_steps_ever))
    log(3, 'action = {}'.format(' '.join(map(lambda x: button_map[x], [i for i,x in enumerate(action) if x]))))
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

