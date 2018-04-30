from envwrappers import BasicEnv
import sys
import argparse
from abc import ABC, abstractmethod

class Agent(ABC):
  def __init__(self, is_remote, game, state, max_timesteps, env_wrapper=BasicEnv, do_pause=False, do_render=False, do_monitor=False):
    if is_remote:
      import gym_remote.client as grc
      self.env = env_wrapper(grc.RemoteEnv('tmp/sock'), max_timesteps=float('inf'), do_pause=False, do_render=False, do_monitor=False)
    else:
      from retro_contest.local import make
      self.env = env_wrapper(make(game=game, state=state), max_timesteps, do_pause, do_render, do_monitor)

  @abstractmethod
  def play(self):
    pass

  @classmethod
  def init_parser(cls, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--game','-g', type=str, default="SonicTheHedgehog-Genesis", help='Name of the game that the agent will play on')
    parser.add_argument('--state','-s', type=str, default="GreenHillZone.Act1", help='Name of the game state that the agent will play on')
    parser.add_argument('--timesteps', '-t', dest='max_timesteps', type=int, default=10000, help="The maximum number of timesteps to use")
    parser.add_argument('--remote', dest='is_remote', default=False, action="store_true", help='Add this flag if the agent should connect to a remote environment (game, state, and timesteps are ignored)')
    parser.add_argument('--render','-r', dest='do_render', default=False, action="store_true", help="Render the observations and take input to control renderings")
    parser.add_argument('--monitor','-m', dest='do_monitor', default=False, action="store_true", help="Produce an unofficial monitor.csv file")
    return parser

  @staticmethod
  def main(agent_class, argv=sys.argv[1:]):
    args = agent_class.init_parser().parse_args(argv)
    agent = agent_class(**vars(args))
    agent.play()
