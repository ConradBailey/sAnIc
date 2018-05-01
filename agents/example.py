#!/usr/bin/env python3.6

import sys
import gym_remote.exceptions as gre
import agent
from envwrappers import BasicEnv

class Example(agent.Agent):
  def __init__(self, is_remote, game, state, max_timesteps, do_render, monitor_path):
    super().__init__(is_remote, game, state, max_timesteps, BasicEnv, do_render, monitor_path)

  def play(self):
    self.env.reset()
    while True:
      action = self.env.action_space.sample()
      ob, reward, done, _ = self.env.step(action)
      if done:
        self.env.reset()


  @classmethod
  def init_parser(cls):
    parser = super().init_parser(description="Example Agent: Randomly does stuff until the trial runs out of timesteps")
    # Here is where I would add agent specific parameters, but there are
    # none for this example
    return parser


if __name__ == '__main__':
  try:
    Example.main(Example)
  except gre.GymRemoteError as e:
    print('exception', e)


