JERK: Just Enough Retained Knowledge
------------------------------------

## About ##
This is my modified version
the
[contest provided baseline](https://github.com/openai/retro-baselines). I
thought it was poorly written, but ripe for improvement.

## How it Works ##
This agent has two courses of action: exploration and exploitation. It
decides on a course of action by a coin flip according to
`EXPLOIT_BIAS`.

A key element of this program is `TrackedEnv`, a wrapper class for gym
environments that retains a memory of every episode it has played and
the corresponding reward.

### Exploration ###
In this phase the agent "explores" the environment with a simple,
deterministic policy. The default behavior is to continuously move to
the right in intervals of `right_steps`, so long as the rewards for
those moves are positive. If the rewards turn negative, then it
backtracks once to the left by `left_steps`, and tries again.

At any time during these moves a jump may be issued with probability
`jump_prob`. The duration of the jump is determined by `jump_repeat`.

### Exploitation ###
In this phase the agent "exploits", i.e. _replays_, the "best"
sequence of moves it has seen so far, as decided by
`get_best_sequence()`. This will **not** be a deterministic replay due
to the stochastic frame skipping, but this agent hinges on the
hypothesis that it will be close enough to result in a good score. If
the replay runs out of moves then no-ops are inserted until the episode
times out.

