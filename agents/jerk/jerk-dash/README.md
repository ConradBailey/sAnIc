JERK with Spin Dashing
----------------------

This is vanilla JERK with a few modifications surrounding a behavior
known as _spin dashing_. Spin dashing occurs when Sonic stands still,
crouches down (Down button held), charges up (Jump button held), and
then dashes (release Jump button)! He curls up into a protective ball
and rolls along the floor in whatever direction he was facing at an
immediately high velocity. If you hit an enemy while spin dashing they
are killed (usually). This is good for getting past loop-de-loops and
half-pipes in Sonic 2. Sonic 3 has some obstacles that can only be
destroyed by hitting them with a spin dash.

Employing this maneuver **does** affect the finite state machine. When
a negative reward is achieved despite trying to travel to the right,
we assume the likely causes are a loop or wall that requires great
speed to overcome, so try spin dashing. If that still does not work,
try back tracking.

Sonic 1 does not have spin dashing, so at the beginning of the
evaluation we should establish whether we have this capability. This
is done by trying to perform a speed dash; if reward is positive the
capability is assumed, otherwise it is assumed incapable. If
incapable, the spin dash is replaced with a running dash: sonic backs
up a little bit for a little runway, then sprints full tilt without
jumping for some number of steps, hopefully clearing the obstacle.
