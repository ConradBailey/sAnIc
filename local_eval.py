#! /usr/bin/env python3.6

import retro_contest.docker

import sys
import argparse
import re
import os

def get_credentials():
  creds_filename = "retro_contest_credentials.dontcommit"
  creds_dir = os.path.split(os.path.realpath(__file__))[0]
  creds_txt = open(os.path.join(creds_dir, creds_filename), 'r').read()
  findings = re.findall("(.*)='(.*)'", creds_txt)

  creds = {}
  for k,v in findings:
    creds[k] = v
  return creds

def make_docker_tag(name, version):
  team_member_name = get_credentials()['TEAM_MEMBER_NAME']
  return '{}/{}:{}'.format(team_member_name, name, version)

def build_agent(path, docker_tag):
  build_cmd = ['build', '-t', docker_tag, path]
  return retro_contest.docker.main(build_cmd)

def test_agent(docker_tag, game, state, results_dir, timestep_limit):
  run_cmd = ['run',
             '--agent', docker_tag,
             '--results-dir', results_dir,
             '--timestep-limit', timestep_limit,
             '--no-nv',
             '--use-host-data',
             game, state]
  return retro_contest.docker.main(run_cmd)

def evaluate(args):
  docker_tag = make_docker_tag(args.name, args.version)
  if args.path:
    build_agent(args.path, docker_tag)
  return test_agent(docker_tag, args.game, args.state,
                    args.results_dir, args.timestep_limit)

def init_parser():
  parser = argparse.ArgumentParser(description="Build agent image and evaluate it locally")
  parser.add_argument('name', type=str, help='Name of agent')
  parser.add_argument('version', type=str, help='Version of agent')
  parser.add_argument('game', type=str, help='Name of the game that the agent will be evaluated on')
  parser.add_argument('state', type=str, help='Name of the game state that the agent will be evaluated on')
  parser.add_argument('timestep_limit', type=str, help='Number of timesteps considered during evaluation')
  parser.add_argument('--path', type=str, help='Path to the agent python script')
  parser.add_argument('--results-dir','-r', type=str, default='results', help='Path to output results')
  return parser

def main(argv=sys.argv[1:]):
  parser = init_parser()
  args = parser.parse_args(argv)
  sys.exit(evaluate(args))

if __name__ == "__main__":
  main()
