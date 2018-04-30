#!/usr/bin/env python3.6

import gym_remote.exceptions as gre
from utils import *
import jerk


class JERK_MoreExplore(jerk.JERK):
  def exploit(self):
    best_sequence = self.get_best_sequence()
    eprint("Exploiting sequence with mean reward {}".format(best_sequence.mean_reward()))
    done = self.perform_actions(best_sequence.actions)
    if done:
      eprint("Ended exploited sequence with total reward {}".format(self.env.episode_reward))
      best_sequence.rewards.append(self.env.episode_reward)
    else:
      eprint("Ran out of actions, exploring end of exploited sequence")
      self.explore()
      eprint("Explored end of an exploited sequence with episode reward {}".format(self.env.episode_reward))


if __name__ == '__main__':
  try:
    JERK_MoreExplore.main(JERK_MoreExplore)
  except gre.GymRemoteError as e:
    print('exception', e)
