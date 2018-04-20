from retro_contest.local import make

import sys

def main(argv=sys.argv[1:]):
  env = make(game = argv[0], state = argv[1])
  print('starting episode')
  env.reset()
  while True:
    action = env.action_space.sample()
    ob, reward, done, _ = env.step(action)
    env.render()
    if done:
      print('episode complete')
      env.reset()


if __name__ == '__main__':
  main()

