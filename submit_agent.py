#! /usr/bin/env python3

import retro_contest.rest

from local_eval import make_docker_tag, build_agent, get_credentials

import sys
import argparse

#def get_credentials():
#  creds_filename = "retro_contest_credentials.dontcommit"
#  creds_dir = os.path.split(os.path.realpath(__file__))[0]
#  creds_txt = open(os.path.join(creds_dir, creds_filename), 'r').read()
#  findings = re.findall("(.*)='(.*')", creds_txt)
#
#  creds = {}
#  for k,v in findings:
#    creds[k] = v
#  return creds
#
#def make_docker_tag(name, version):
#  return '{}:v{}'.format(name, version)
#
#def build_agent(path, docker_tag):
#  build_cmd = ['build', '-t', docker_tag, path]
#  return retro_contest.docker.main(build_cmd)

def contest_login(email, password):
  login_cmd = ['login',
               '--server', 'https://contest.openai.com',
               '--email', email,
               '--password', password]
  return retro_contest.rest.main(login_cmd)

def contest_submit(docker_tag):
  submit_cmd = ['job', 'submit',
               '--tag', docker_tag]
  return retro_contest.rest.main(submit_cmd)

def contest_logout():
  logout_cmd = ['logout']
  return retro_contest.rest.main(logout_cmd)

def submit(args):
  docker_tag = make_docker_tag(args.name, args.version)
  if args.path:
    build_agent(args.path, docker_tag)

  creds = get_credentials()
  email = creds['TEAM_EMAIL_ADDR']
  password = creds['TEAM_PASSWORD']
  contest_login(email, password)
  contest_submit(docker_tag)
  contest_logout()
  return 0

def init_parser():
  parser = argparse.ArgumentParser(description="Submit an agent image for contest evaluation")
  parser.add_argument('name', type=str, help='Name of agent')
  parser.add_argument('version', type=str, help='Version of agent')
  parser.add_argument('--path','-p', type=str, help='Path to the agent python script')
  return parser

def main(argv=sys.argv[1:]):
  parser = init_parser()
  args = parser.parse_args(argv)
  sys.exit(submit(args))

if __name__ == "__main__":
  main()
