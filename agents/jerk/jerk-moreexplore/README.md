JERK -- More Exploration
------------------------

In this improved version of JERK the exploitation phase does not end
with no-ops if the exploited sequence is insufficient. Instead the
agent transfers control to the exploration phase.

The hypothesis here is that those no-ops are just wasted timesteps
where no learning is occurring. We should utilize those timesteps
through the exploration phase, which should be especially effective
since the exploitation phase has, hypothetically, given it a good head
start.
