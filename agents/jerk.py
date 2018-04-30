#!/usr/bin/env python3.6

import gym_remote.exceptions as gre
import random
import sys
from utils import *
import agent
from envwrappers import HistoriedEnv, Sequence


class JERK(agent.Agent):
  def __init__(self, is_remote, game, state, max_timesteps, do_render, do_monitor,
               exploit_bias, jump_repeat, jump_prob, right_steps, left_steps):
    super().__init__(is_remote, game, state, max_timesteps, HistoriedEnv, do_pause=do_render, do_render=do_render, do_monitor=do_monitor)
    self.sequences = []
    self.exploit_bias = exploit_bias
    self.jump_repeat = jump_repeat
    self.jump_prob = jump_prob
    self.right_steps = right_steps
    self.left_steps = left_steps


  def play(self):
    while True:
      self.env.reset()
      if self.do_exploit():
        self.exploit()
      else:
        self.explore()


  # Coin flip to decide whether to exploit or explore
  def do_exploit(self):
    if self.env.trial_timesteps == 0:
      return False

    exploit_prob = self.exploit_bias + (self.env.trial_timesteps / self.env.max_timesteps)
    eprint("Flipped explot coin, exploit_bias = {}    exploit_prob = {}".format(self.exploit_bias, exploit_prob))
    return random.random() < exploit_prob


  def exploit(self):
    best_sequence = self.get_best_sequence()
    eprint("Exploiting sequence with mean reward {}".format(best_sequence.mean_reward()))
    done = self.perform_actions(best_sequence.actions)
    if not done:
      eprint("Ran out of actions, inserting no-ops")
      while not done:
        obs, rew, done, _ = self.env.step([0]*12)

    eprint("Ended exploited sequence with total reward {}".format(self.env.episode_reward))
    best_sequence.rewards.append(self.env.episode_reward)


  # Determine what the best sequence of actions so far has been
  # Room for improvement. Think confidence intervals
  def get_best_sequence(self):
    return max(self.sequences, key=lambda x: x.mean_reward())


  # Perform all the actions of some sequence
  def perform_actions(self, actions):
    for action in actions:
      _, _, done, _ = self.env.step(action)
      if done:
        break

    return done


  ### Explore ###
  def explore(self):
    eprint("Exploring a new vein in the action space")

    done = False
    while not done:
      eprint("moving right {} steps".format(self.right_steps))
      reward, done = self.move('right', self.right_steps)
      if not done and reward <= 0:
        eprint("Moving left {} steps because a negative reward was detective".format(self.left_steps))
        _, done = self.move('left', self.left_steps)
    eprint("Finished exploration with a total reward of {}".format(self.env.episode_reward))
    self.sequences.append(self.env.history.best_sequence())

  # Move Sonic to the right or the left with coin-flips for jumping
  def move(self, movement, steps=0):
    move_reward = 0

    jump_steps = 0
    for step in range(steps):
      action, jump_steps = self.make_action(movement, jump_steps)

      _, reward, done, _ = self.env.step(action)
      move_reward += reward
      if done:
        break

    return move_reward, done


  # Construct the actual action data structure
  def make_action(self, movement, jump_steps):
    action = [False]*12
    # Designate direction
    if movement == 'left':
      action[6] = True
    elif movement == 'right':
      action[7] = True

    # Choose whether to jump
    if jump_steps <= 0:
      if random.random() < self.jump_prob:
        jump_steps = self.jump_repeat
    else:
        action[0] = True
        jump_steps -= 1

    return action, jump_steps


  @classmethod
  def init_parser(cls):
    parser = agent.Agent.init_parser(description="JERK (Just Enough Retained Knowledge) Agent")
    parser.add_argument('--exploit-bias','-eb', type=float, default=0, help="Used in the coinflip for  exploit vs explore")
    parser.add_argument('--jump-repeat','-jr', type=int, default=4, help="Number of timesteps the jump button should be held when performing a jump")
    parser.add_argument('--jump-prob','-jp', type=float, default=.1, help="The probability (as a decimal) of a jump occuring while moveing left or right")
    parser.add_argument('--right-steps','-rs', type=int, default=100, help="The number of timesteps to use for one right travel")
    parser.add_argument('--left-steps','-ls', type=int, default=70, help="The number of timesteps to use for one left travel")
    return parser


if __name__ == '__main__':
  try:
    JERK.main(JERK)
  except gre.GymRemoteError as e:
    print('exception', e)
