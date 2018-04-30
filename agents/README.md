Agents
------

In this folder you will find all of the agents created thus far. All
agents must be placed here.

All agents should inherit from `Agent` somewhere in their
lineage. `Agent` provides the following usage as a basis
```
usage: agentname.py [-h] [--game GAME] [--state STATE]
                  [--timesteps MAX_TIMESTEPS] [--remote] [--render]

Short description of the agent

optional arguments:
  -h, --help            show this help message and exit
  --game GAME, -g GAME  Name of the game that the agent will play on
  --state STATE, -s STATE
                        Name of the game state that the agent will play on
  --timesteps MAX_TIMESTEPS, -t MAX_TIMESTEPS
                        The maximum number of timesteps to use
  --remote              Add this flag if the agent should connect to a remote
                        environment (game, state, and timesteps are ignored)
  --render, -r          Render the observations and take input to control
                        renderings
```

You can use these flags and the agent modules to debug agents locally
and render the actions, e.g. `$ ./example.py --render`.

To evaluate the agent under contest conditions and produce `bk2`
output use `local_eval.py` which will automatically pass the
`--render` flag along.

To submit the agent to the contest meet with Conrad.

## Example Agent ##
This is an example of an agent that plays by choosing random actions
at every step. As you might expect, this isn't very effective. A
slightly better approach for Sonic games is to always go to the right
with a line like `action[7] = 1`.

## JERK ##
### About ###
This is my modified version
the
[contest provided baseline](https://github.com/openai/retro-baselines). I
thought it was poorly written, but ripe for improvement.

You can see how easy it is to modify by looking at
`jerk_moreexploit.py`, `jerk_moreexplore.py`, and especially
`jerk_exploreexploit.py`.

### How it Works ###
This agent has two courses of action: exploration and exploitation. It
decides on a course of action by a coin flip according to
`exploit_bias`.

A key element of this program is `HistoriedEnv`, a wrapper class for gym
environments that retains a memory of every episode it has played and
the corresponding reward.

#### Exploration ####
In this phase the agent "explores" the environment with a simple,
deterministic policy. The default behavior is to continuously move to
the right in intervals of `right_steps`, so long as the rewards for
those moves are positive. If the rewards turn negative, then it
backtracks once to the left by `left_steps`, and tries again.

At any time during these moves a jump may be issued with probability
`jump_prob`. The duration of the jump is determined by `jump_repeat`.

#### Exploitation ####
In this phase the agent "exploits", i.e. _replays_, the "best"
sequence of moves it has seen so far, as decided by
`get_best_sequence()`. This will **not** be a deterministic replay due
to the stochastic frame skipping, but this agent hinges on the
hypothesis that it will be close enough to result in a good score. If
the replay runs out of moves then no-ops are inserted until the episode
times out.

### Modifications ###
#### More Exploit ####
In this modification, if an agent reaches the end of a level
(i.e. reward > 9000), then `exploit_bias` is switched to `1`
guaranteeing exploitation in subsequent episodes. If during these
subsequent exploitations the agent _does not_ reach the end of the
level (i.e. reward < 9000) then `exploit_bias` is reverted to its
original value.

The hypothesis behind this approach is that if a successful sequence
of moves is found, why bother exploring? Just keep doing _whatever
works_! But if that stops working, then perhaps it's not a robust
sequence and we should explore other options.

#### More Explore ####
In this improved version of JERK the exploitation phase does not end
with no-ops if the exploited sequence is insufficient. Instead the
agent transfers control to the exploration phase.

The hypothesis here is that those no-ops are just wasted timesteps
where no learning is occurring. We should utilize those timesteps
through the exploration phase, which should be especially effective
since the exploitation phase has, hypothetically, given it a good head
start.

#### Explore Exploit ####
This simply combines the "More Explore" and "More Exploit"
modifications. See how easily this is done with inheritance; virtually
no new code is necessary!

#### Dash ####
This is vanilla JERK with a few modifications surrounding a behavior
known as _spin dashing_. Spin dashing occurs when Sonic stands still,
crouches down (Down button held), charges up (Jump button held), and
then dashes (release Jump button)! He curls up into a protective ball
and rolls along the floor in whatever direction he was facing at an
immediately high velocity. If you hit an enemy while spin dashing they
are killed (usually). This is good for getting past loop-de-loops and
half-pipes in _Sonic The Hedgehog 2_. _Sonic And Knuckles 3_ has some
obstacles that can only be destroyed by hitting them with a spin dash.

Employing this maneuver **does** affect the finite state machine. When
a negative reward is achieved despite trying to travel to the right,
we assume the likely causes are a loop or wall that requires great
speed to overcome, so try spin dashing. If that still does not work,
try back tracking.

The original _Sonic The Hedgehog_ does not have spin dashing, so at
the beginning of the trial we should establish whether we have this
capability. This is done by trying to perform a speed dash; if reward
is positive the capability is assumed, otherwise it is assumed
incapable. If incapable, the spin dash is replaced with a running
dash: sonic backs up a little bit for a little runway, then sprints
full tilt without jumping for some number of steps, hopefully clearing
the obstacle.
