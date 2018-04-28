#! /usr/bin/env python3.6

import sys
import argparse
import os
from multiprocessing import Pool

from local_eval import make_docker_tag, build_agent, test_agent

class Tester:
  def __init__(self, docker_tag, results_dir, timestep_limit):
    self.docker_tag = docker_tag
    self.results_dir = results_dir
    self.timestep_limit = timestep_limit

  def __call__(self, game_state):
    game, state = game_state
    test_results_dir = os.path.join(self.results_dir, '{}_{}-results'.format(game, state))
    if os.path.exists(test_results_dir):
      num = 0
      while os.path.exists(test_results_dir):
        test_results_dir = os.path.join(self.results_dir, '{}_{}_{}-results'.format(game, state, num))
        num += 1
    test_agent(self.docker_tag, game, state, test_results_dir, self.timestep_limit)

def test(args):
  docker_tag = make_docker_tag(args.name, args.version)
  if args.path:
    build_agent(args.path, docker_tag)

  tests = [x.split() for x in open(args.tests_file, 'r').readlines()]
  os.mkdir(args.results_dir)
  with Pool(args.nprocs) as pool:
    pool.map(Tester(docker_tag, args.results_dir, args.timestep_limit), tests)

def init_parser():
  parser = argparse.ArgumentParser(description="Run a trial with some agent for every state in a test set")
  parser.add_argument('tests_file', type=str, help="List of states to test on. One game and state per line, separated by whitespace")
  parser.add_argument('timestep_limit', type=str, help="Timestep limit for the trial")
  parser.add_argument('name', type=str, help='Name of agent')
  parser.add_argument('version', type=str, help='Version of agent')
  parser.add_argument('--path','-p', type=str, help='Path to the agent python script')
  parser.add_argument('--results_dir','-r', type=str, default='results', help='Path to output results')
  parser.add_argument('--nprocs','-n', type=int, default=1, help='Number of trials to run in parallel')
  return parser

def main(argv=sys.argv[1:]):
  parser = init_parser()
  args = parser.parse_args(argv)
  sys.exit(test(args))


if __name__ == "__main__":
  main()
