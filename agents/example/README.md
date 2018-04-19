# Agent Script and Image Example #
This is an example of an agent that plays by choosing random actions
at every step. As you might expect, this isn't very effective. A
slightly better approach for Sonic games is to always go to the right
with a line like `action[7] = 1`.

You can try this example out locally with
`$ local_eval.sh example.docker example 1 SonicTheHedgehog-Genesis GreenHillZone.Act1 10000`.
This will build the image and run 10000 random actions.

To submit this to the contest for evaluation you would run
`$ submit_agent.sh example.docker example 1`. _Please **don't**_ do
this though because it is a terrible agent.
