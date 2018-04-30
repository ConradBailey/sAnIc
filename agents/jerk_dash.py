#!/usr/bin/env python3.6

import gym_remote.exceptions as gre
from utils import *
import jerk


class JERK_Dash(jerk.JERK):
  def play(self):
    self.env.reset()
    self.set_dash()

    while True:
      self.env.reset()
      if self.do_exploit():
        self.exploit()
      else:
        self.explore()


  def explore(self):
    eprint("Exploring a new vein in the action space")

    done = False
    while not done:
      eprint("moving right {} steps".format(self.right_steps))
      reward, done = self.move('right', self.right_steps)
      if not done and reward <= 0:
        eprint("Negative reward detected. Attempting spin dash")
        reward, done = self.dash()
      if not done and reward <= 0:
        eprint("Negative reward detected. Moving left {} steps".format(self.left_steps))
        _, done = self.move('left', self.left_steps)
    eprint("Finished exploration with a total reward of {}".format(self.env.episode_reward))
    self.sequences.append(self.env.history.best_sequence())


  def running_dash(self):
    eprint("performing running dash")
    reward_start = self.env.episode_reward
    action = [False]*12
    done = False

    eprint("  Backing up")
    # Back up a little bit
    action[6] = True
    for _ in range(30):
      if done:
        break
      _, reward, done, _ = self.env.step(action)
    action[6] = False

    eprint("  Sprinting right")
    # Sprint to the right, no jumps
    action[7] = True
    for _ in range(60):
      if done:
        break
      _, reward, done, _ = self.env.step(action)
    while reward > 0:
      if done:
        break
      _, reward, done, _ = self.env.step(action)
    action[7] = False

    return self.env.episode_reward - reward_start, done


  def spin_dash(self):
    eprint("performing spin dash")
    reward_start = self.env.episode_reward
    action = [False]*12
    done = False

    # Alternate back and forth
    action[6] = True
    for _ in range(10):
      if done:
        break
      _, reward, done, _ = self.env.step(action)
      action[6] = not action[6]
      action[7] = not action[7]
    action = [False]*12

    # Turn to the right
    action[7] = True
    for _ in range(7):
      if done:
        break
      _, reward, done, _ = self.env.step(action)
    action[7] = False

    # Stop Moving
    action = [False] * 12
    for _ in range(20):
      if done:
        break
      _, reward, done, _ = self.env.step(action)

    # Crouch down to prepare charge up
    for _ in range(10):
      if done:
        break
      action[5] = True
      _, reward, done, _ = self.env.step(action)

    # Charge up to prepare for dash
    action[0] = True
    for _ in range(20):
      if done:
        break;
      _, reward, done, _ = self.env.step(action)

    # Release buttons and do the dash
    if not done:
      action[0] = False
      action[5] = False
      _, reward, done, _ = self.env.step(action)

    # Let it go while it's good
    for _ in range(10):
      if done:
        break
      _, reward, done, _ = self.env.step(action)

    while reward > 0 and not done:
      _, reward, done, _ = self.env.step(action)

    return self.env.episode_reward - reward_start, done


  def set_dash(self):
    eprint("Testing spin dash")
    reward_start = self.env.episode_reward
    action = [False]*12
    done = False

    # Crouch down to prepare charge up
    for _ in range(10):
      if done:
        break
      action[5] = True
      _, reward, done, _ = self.env.step(action)

    # Charge up to prepare for dash
    action[0] = True
    for _ in range(10):
      if done:
        break;
      _, reward, done, _ = self.env.step(action)

    # Release buttons and do the dash
    if not done:
      action[0] = False
      action[5] = False
      _, reward, done, _ = self.env.step(action)


    if reward > 0:
      eprint("setting dash as spin_dash")
      self.dash = self.spin_dash
    else:
      eprint("setting dash as running_dash")
      self.dash = self.running_dash

    print("dashing reward = {}".format(self.env.episode_reward - reward_start))

    # Try to die quickly
    self.explore()
    self.env.reset()


if __name__ == '__main__':
  try:
    JERK_Dash.main(JERK_Dash)
  except gre.GymRemoteError as e:
    print('exception', e)
