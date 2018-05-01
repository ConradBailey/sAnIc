# sAnIc #
This repository holds our work for
the [OpenAI Retro Contest](https://contest.openai.com/). If you're a
team member looking for information about working on the project,
visit
the
[How To](https://gitlab.com/sAnIc-ND/sAnIc#how-to-do-stuff-relevant-to-this-project) section. If
you are a visitor looking for information about our work, visit
the [project website](https://sanic-nd.gitlab.io/sAnIc/)!

#### Dependencies ####
* python 3.6
* pip 3.6
* virtualenv (download via `$ pip3.6 install virtualenv`)
* git
* docker
  * [Ubuntu instructions](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
  * [Mac Instructions](https://store.docker.com/editions/community/docker-ce-desktop-mac)

#### Requirements ####
* 64-bit Architecture

## How To Do Stuff Relevant To This Project ##
### Table of Contents ###
* [Vocabulary](https://gitlab.com/sAnIc-ND/sAnIc#vocabulary)
* [Assumptions](https://gitlab.com/sAnIc-ND/sAnIc#assumptions)
* [Contribute to the Project](https://gitlab.com/sAnIc-ND/sAnIc#contribute-to-the-project)
* [Install the Virtual Environment](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)
* [Work on the Website](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)
* [Start a Jupyter Notebook in the Virtualenv](https://gitlab.com/sAnIc-ND/sAnIc#start-a-jupyter-notebook-in-the-virtualenv)
* [Creating an Agent](https://gitlab.com/sAnIc-ND/sAnIc#creating-an-agent)
* [Simulate an Agent Locally](https://gitlab.com/sAnIc-ND/sAnIc#simulate-an-agent-locally)
* [Analyze Results](https://gitlab.com/sAnIc-ND/sAnIc#analyze-results)
* [Evaluate an Agent On Many Tests](https://gitlab.com/sAnIc-ND/sAnIc#evaluate-an-agent-on-many-tests)
* [Analyze a Batch of Results](https://gitlab.com/sAnIc-ND/sAnIc#analyze-a-batch-of-results)
* [Submit a Job](https://gitlab.com/sAnIc-ND/sAnIc#submit-a-job)
* [Convert `.bk2` Files to `.mp4` Videos](https://gitlab.com/sAnIc-ND/sAnIc#convert-bk2-files-to-mp4-videos)
* [Resources](https://gitlab.com/sAnIc-ND/sAnIc#resources)

### Vocabulary ###
There are some novel elements to this project so a decisive vocabulary
is necessary for effective communication and cohesive code.

**NOTE**: These definitions are our own; other documentation often has
inconsistent vocabularies. This vocabulary is generally in alignment
with
the
[white paper](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/retro-contest/gotta_learn_fast_report.pdf) for
the contest.
* **Environment**: An object instance returned from a call to
  `retro_contest.local.make` for local environments,
  `gym_remote.client.RemoteEnv` for remote environments, or some
  wrapper. This object handles the game simulation and provides the
  interface to it through methods like `.reset()`, `.step()`,
  `.render()`, and others. A _remote_ environment is created and
  managed by a Docker container in the background; this is done when
  submitting an agent to the contest or simulating an agent
  submission. A _local_ environment is created and managed by the
  agent itself.
* **Episode**: One attempt at completing a level. An **episode** ends
  when the player dies, completes the level, or runs out of timesteps
  (4500). This is signalled in the `done` value returned by
  `environment.step()`. An episode begins with a call to
  `environment.reset()` which should only be called immediately after
  environment creation or when `done` is `True`.
* **Agent**: A script that simulates episode after episode of some
  level for some number of timesteps. If the agent uses a local
  environment then it is responsible for setting and abiding by the
  timestep limit and outputting a `monitor.csv`. If the agent uses a
  remote environment, then it doesn't need to worry about the timestep
  limit; it can operate as though it's running infinitely and silently
  while the limit and `monitor.csv` output is taken care of remotely.
* **State**: Imagine the common understanding of _level_ in the
  context of videogames. Example: `Green Hill Zone - Act 1` is the
  first state of the game `Sonic The Hedgehog`. The begin far on the
  left and are considered complete when some horizontal displacement
  is achieved.
* **Game**: A collection of levels and control definitions. These are
  implemented via ROMs that are copied directly from the original game
  cartridges. For instance: `Sonic The Hedgehog 2` has
  a [Spin Dash](http://sonic.wikia.com/wiki/Spin_Dash) move, but
  `Sonic The Hedgehog` does not.
* **Trial**: A trial is defined by an agent, a level, and a timestep
  limit. During a trial the agent will simulate play in that level,
  restarting as necessary, until the timestep limit is reached.
* **Timestep**: The smallest unit of time in a simulation. A timestep
  occurs when some action is passed to `environment.step()`; the
  action is enacted for four real game frames (+/- 1) during one
  timestep. One timestep is approx. 1/15 of a second of wall-clock
  time in the game, so the episode limit of 4500 timesteps is approx 5
  minutes of real gameplay.
* **Test Set**: A list of game-state tuples for the purposes of
  experiments and testing in general.
* **Experiment**: An experiment should be designed to explore the
  behavior of a range of values for a single parameter of an agent. An
  experiment requires an agent, values for the static parameters of
  that agent, a range of values for the dynamic variable of that
  agent, a test set, a trial limit, and a timestep limit. An
  experiment will run trials according to the timestep limit until the
  trial limit is exceeded for every value in the dynamic variable
  range and for every level in the test set (think nested loops).
* **Observation**: The graphical data of a frame. This is the first
  element in the tuple returned by a call to `environment.step()`. It
  is a 320x224x3 array of RGB pixel data.
* **Action**: An 12 element array of binary values (0/1 or
  `True`/`False`) corresponding to buttons on a Sega Genesis
  controller such that ON means pressed and vice versa. The mapping of
  index to button is
  `{0: JUMP, 1: JUMP, 2: (ignored), 3: (ignored), 4: UP, 5: DOWN, 6: LEFT, 7: RIGHT, 8: JUMP, 9: (ignored), 10: (ignored), 11: (ignored)}`
  (_Sonic_ does not make use of all the buttons, and there are redundancies for jumping).
  An action is performed by passing as an argument to
  `environment.step()`.
* **Action Space**: The set of possible actions to take in an environment.
* **Reward**: After every action (a.k.a. call to `environment.step()`,
  a reward for the action is presented by the environment as the
  second item in the tuple return from `environment.step()`. This
  magnitude of this reward is proportional to the horizontal
  displacement achieved by the action and positive if to the right and
  negative if to the left.
* **Score**: Every episode is given a score at the end. This score is
  the sum total of all the rewards from the actions that took place
  during the episode (max 9000) plus a bonus for speed (theoretical
  max 1000). Every trial is given a score which is the mean of the
  scores of all the episodes that completed. The contest evaluation
  system awards an agent a total score which is the mean of the
  episode scores for every level it tests.
* **Container / Image**: See
  this
  [Stack Overflow post](https://stackoverflow.com/questions/21498832/in-docker-whats-the-difference-between-a-container-and-an-image). In
  this documentation "container" is used exclusively and probably not
  precisely. It's not that important for our purposes.

### Assumptions ###
* You're keeping everything for the project in a directory called
  `sAnIc`. This is the default after having done `git clone` for this
  repository or a fork of it.
* ROMs are stored in a directory called `roms` under `sAnIc`, i.e. at
  `sAnIc/roms`
* You're using a shell thats "`bash`-compatible". That means no `csh`,
  `tcsh`, `ksh`, etc. The scripts are targeted at POSIX `sh`, but
  using `bash` is the safest choice.
* You're developing in Python 3. Don't use Python 2. *Dont use `pip`
  or `pip2`; _use `pip3.6`_* just to be explicitly compliant. Use
  `#!/usr/bin/env python3.6` for your shebangs.
* You've installed the dependencies yourself. You need how to
  figure this out for your own environment, e.g. Ubuntu will need
  calls to `$ sudo apt-get install` or something.

### Contribute to the Project ###
Things can get really messy with dependencies and outside libraries
and everything else. For that reason we will use pull requests to
contribute work instead of straight pushes to the repo.
1. [Fork](https://docs.gitlab.com/ee/gitlab-basics/fork-project.html) The Project
   * Visit the [main project repo](https://gitlab.com/sAnIc-ND/sAnIc)
     and click `Fork` just to the left and below the Sanic icon.
   * This may give you a list of entities to fork it with, if so then
     click the entity representing your personal account.
   * This should create new repo just like the original, but owned by
     you, and it should have taken you to that repo's main page. If
     not try to find the new repo in your account's list of
     repositories.
   * Now clone this repository of yours onto your local machine with
     the link provided just below the icon.
2. Add an Upstream [Remote](https://www.atlassian.com/git/tutorials/syncing)
   * Adding this allows you to stay up to date by fetching code from
     the main project repo and merging it into your forked repo
   * `cd` to your local copy of the forked repo and run  
   `$ git remote add upstream https://gitlab.com/sAnIc-ND/sAnIc.git`.
3. Update the Fork
   * Make sure you're on the `master` branch with `git status`, then
     run `$ git pull upstream master`. This will perform the fetch and
     merge operations. Unless you're developing on `master` (**at your
     own risk**) there should not be any merge conflicts.
4. Make a [Branch](https://www.atlassian.com/git/tutorials/using-branches)
   * Make a branch to do your work in. Your branch should be named
     after the work done on it, like a feature or bug fix.
   * `cd` to your local copy of your forked repo. Run  
     `$ git checkout -b Name_of_Branch upstream/master`.
5. Do the Work
   * Do whatever work you want to do. Make an agent with a new
	 algorithm. Do new visualizations or analytics for an old
	 agent. [Work on the website](https://gitlab.com/sAnIc-ND/sAnIc#work-on-the-website). Whatever!
6. Stage Your Changes
   * Stage your changes using calls to `git add` and `git rm` if necessary.
7. Commit Your Changes
   * Commit your changes with `git commit`. Go back to step 5 afterwards
	 if you're splitting the work into multiple commits.
8. Check for Updates One Last Time
   * Run `$ git fetch upstream master`. This will retrieve any new
     code from upstream, but it won't really do anything with it.
   * Run `$ git rebase upstream/master Name_of_Branch` or
     whatever. This takes your work and sort of re-does it all on top
     of the most up to date code. That way it is easier to merge into
     the main project!
9. Push Your Changes
   * Push your changes to your personal repo with `$ git push
	 origin`. This will add a branch named `Name_of_Branch` or whatever
	 to your fork on GitLab. This branch is accessible through the
	 `Branches` link in the `Repository` menu on the left side of the
	 main page for your fork on GitLab.
10. Create a [Merge Request](https://docs.gitlab.com/ee/gitlab-basics/add-merge-request.html)
    * If everything looks good to you on the branch then it's time to
      start merging it into the main repo
    * Visit
      the
      [main project page](https://docs.gitlab.com/ee/gitlab-basics/add-merge-request.html) and
      click on the `+` icon below and to the right of the sAnIc icon,
      then press `New merge request`. This should take you to a page
      for merge request creation with boxes for `Source branch` and
      `Target branch`.
    * Under `Source branch` the `Source project` on the left should
      read `YourUsername/sAnIc` and the `Source branch` should select
      `Name_of_Branch` or whatever. Under `Target branch` the `Target
      project` on the left should read `sAnIc-ND/sAnIc` and the `Target
      branch` should be `master`. Assuming that is all true, click
      `Compare branches and continue` in the bottom left.
    * On this page make sure the title is clear and give a description
      of the work. Try to be very thorough. The merges need to be
      reviewed so let the reviewer know all of the information that
      they might find useful about what you're trying to
      contribute. Use good formatting too; the description box supports
      Markdown.
    * Do not assign the merge to anyone
    * You can check `Remove source branch when merge request is
      accepted.` if you'd like the branch you pushed to `origin`
      deleted from GitLab.
    * Press `Submit merge request`
11. Merge Review
	* If upon review your work needs any modifications, perform them
	  on your local machine, stage, commit, update, and push them just
	  as before, but **do not** make another merge request. The
	  original merge request will be updated with your new
	  commits. The reviewer should help you through this process.
12. Eventually your work will be merged. You should go back to the
    local clone of your fork, checkout the `master` branch, and pull
    from upstream again (step 3). You're now free to delete
    `Name_of_Branch` or whatever with `$ git branch -d Name_of_Branch`
    or whatever.

### Install the Virtual Environment ###
1. Acquire the ROMs from Conrad. We cannot put these in a public repo;
   they are proprietary. On that note, **DO NOT COMMIT/PUSH THESE TO
   YOUR REPO!!** I assume they are stored in `sAnIc/roms`. If you
   keep this convention, then that directory will be ignored thanks to
   `.gitignore`
2. Run `$ ./install.sh roms`. This will check for requirements, create
   a virtual environment for Python 3 development, install necessary
   packages, download
   the [retro-contest](https://github.com/openai/retro-contest)
   repository, and install those tools as well.
3. Run `$ source venv/bin/activate`. This imports the virtualenv
   environment into your shell instance and should prepend `(venv)` to
   your shell prompt. That means anything installed with `pip3.6` will
   be local to this virtualenv and can be cleanly swept away with `rm
   -r venv`. To get out of this environment when you're done working
   on the project run `deactivate`, it's that simple.

### Work on the Website ###
All of the website files are found in the `public` directory.
0. Consider using the branch and merge workflow
   from
   [Contributing to the Project](https://gitlab.com/sAnIc-ND/sAnIc#contribute-to-the-project).
1. Edit, add, or delete files in `public`
2. Test your changes locally, i.e. review your changes in your browser
3. Commit and push your changes. A pipeline will run that publishes
   your changes. When that has completed you can review the published
   changes on at your local copy of the website,
   `https://yourusername.gitlab.io/sAnIc/`.
4. When you're happy with your changes create a merge request (see
   [here](https://gitlab.com/sAnIc-ND/sAnIc#contribute-to-the-project)).

### Start a Jupyter Notebook in the Virtualenv ###
Jupyter notebooks are good for data analysis because you can re-run
portions of code as needed, without having to recreate or save and
load large data structures.

**IMPORTANT_NOTE**: steps 1 to 3 do not need to be repeated. After
creating the kernel it can be reused at will.

0. Install Jupyter for your distribution
1. Activate the virtualenv (see step
   3
   [here](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)).
2. Run `$ ipython kernel install --user --name=sAnIc`. This will create
   a kernel called `sAnIc` that we will use to make a notebook in the
   next step.
3. Outside of the virualenv (i.e. `(venv)` should not be prepended to
   your shell prompt) run `$ jupyter notebook`. This will start the
   notebook server and print some text with a link.  Copy this link to
   the address bar in your internet browser.
4. Navigate to the place you'd like to put the notebook and click
   'new' in the upper right corner; this will open a new context. In
   that context, under 'Notebook:' click 'sAnIc'; this designates the
   kernel we created earlier, giving you access to the virtualenv's
   resources.
5. Use the notebook!

### Creating an Agent ###
First and foremost, look at
[`agents/example.py`](https://gitlab.com/sAnIc-ND/sAnIc/tree/master/agents/example.py)
for reference on the most basic implementation of an agent.

All agent modules must live directly in
the [`agents`](https://gitlab.com/sAnIc-ND/sAnIc/blob/master/agents)
folder, and not in any subdirectory, to the packaging necessary for
deployment. All agents need to inherit somewhere in their lineage from
the `Agent` class found
in
[`agent.py`](https://gitlab.com/sAnIc-ND/sAnIc/blob/master/agents/agent.py). This
provides the basic functionalities, `main` implementation, and command
line parsing tools. There are 4 basic parts to an agent.

1. **Agent Class Definition and `__init__`**
   * Don't forget the shebang on the first line `#!/usr/bin/env python3.6`
   * All agent class definitions should look like  
	 `class AgentBeingDefined(AgentOrAgentChild)`. Multiple inheritance can be useful
     here
     (see
     [agents/jerk-exploreexploit.py](https://gitlab.com/sAnIc-ND/sAnIc/blob/master/agents/jerk_exploreexploit.py)).
   * `__init__` may be inherited if the agent being defined does not
     require any more parameters than its parents. However, if new
     parameters are being introduced by the agent being defined, then
     `__init__` must be implemented to handle them.
   * `__init__` should first take as arguments the necessities for
     agent creation (`is_remote`, `game`, `state`, `max_timesteps`,
     `do_render`, `do_monitor`) followed by any parameters necessary
     for the parent `__init__` method, finally ending with parameters
     specific to the agent being defined.
	 * The first line in the body of `__init__` should be a call to
       the parent class `__init__` that looks like  
	   `super().__init__(is_remote, game, state, max_timesteps, env_wrapper, do_pause, do_render, do_monitor, any_other_parent_args...)`
	   where `env_wrapper` is some class that maintains useful
       environment information for the agent being defined
       (see
       [`agents/jerk.py`'s use of `HistoriedEnv`](https://gitlab.com/sAnIc-ND/sAnIc/blob/master/agents#jerk)). The
       default value (`BasicEnv`) will suffice in most cases.
	 * `__init__` should then take care of any initialization
       procedures specific to the agent being defined.
2. **The `play()` Method**
   * This method may be inherited from a concrete class, but cannot be
     inherited from the abstract `Agent` class.
   * It should be an **infinite** loop that essentially plays the
     game. Remember that `env.reset()` must be called once before any
     calls to `env.step()`, and `env.reset()` must be called when
     `done` is `True`.
3. **The `init_parser()` Method**
	* This method may be inherited if no extra parameters are
     necessary for the agent being defined.
	* The first line in this methods body should be a call to the
     parent definition that looks like  
	 `parser = super().init_parser("description of class being defined")`
	* Finally you should add parameters specific to the agent being
     defined with calls to `parser.add_argument` and finally `return
     parser`.
4. **`main()` Invocation**
   * You can rely on `Agent`'s `main()` static method. The bottom of
     your agent should look like

	     ```python
		 if __name__ == '__main__':
		   try:
		     AgentBeingDefined.main(AgentBeingDefined)
		   except gre.GymRemoteError as e:
		     print('exception', e)
		 ```
   * This will call the `main` inherited from `Agent` with
     `AgentBeingDefined` as an argument so that the `main()` body will
     instantiate an agent of type `AgentBeingDefined` and call that
     instantiation's `play()` method.

Once all of that is done you can run your agent right from the command
line with `$ ./agentyoudefined.py`. `Agent` provides some nice flags
like `--render` to watch and control the agent at work and `--monitor`
to produce a `monitor.csv`. See `$ ./agentyoudefined.py --help` for
the complete list.

### Simulate an Agent Locally ###
This process will mimic the remote environment used for official
scoring when submitting a job.  It is important to do this
before
[submitting the agent as a job](https://gitlab.com/sAnIc-ND/sAnIc#submit-a-job) so
that you don't waste time finding runtime errors after uploading to
the server.
1. Activate your virtual environment (see step
   3
   [here](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)).
2. Acquire a credentials file from Conrad. This contains sensitive
   passwords and stuff. **DO NOT COMMIT/PUSH THIS FILE!!** If you keep
   the name `retro_contest_credentials.dontcommit` then it will be
   safely ignored thanks to `.gitignore`. If you guys are paranoid,
   then we can work out some encryption, but for now just be careful.
4. Run `$ local_eval.py [--results_dir RESULTS_DIR] [--args ARGS] path name version game state timestep_limit`'.
   This will
   + Create a Docker container with the agent at `path` installed as a Python package.
   + Tag that container as `team_member_name/name:version`. The `name`
     should characterize the implementation (e.g. DNN for deep neural
     net) and `version` is a convenient way to iteratively experiment
     on an implementation.
   + Simulate a contest run using the new container for the agent and
     the specified game and state for the environment. It will pass on
     `--args` if provided to the agent invocation, like parameter
     values (`--remote` is automatically provided).

     The `timestep_limit` determines how many time steps
     (i.e. calls to `env.step()`) the evaluation is alloted. It doesn't
     matter how many times Sonic dies, wins, or runs out of time; the
     evaluation only has the allotted amount of steps to achieve the
     highest average score possible. The contest sets this to one
     million steps; you'll have to play around with this value to fit
     your experimentation needs.
5. This will output a folder named `results` (by default. see
   `--results-dir`) in the working directory. In this directory there
   are useful files:
   + `agent_stderr.txt` and `agent_stdout.txt`: This is where you'll
     find any debugging output or errors produced by your agent.
   + `remote-stderr.txt` and `remote-stdout.txt`: This is where you'll
     find output and errors from the remote environment provided by
     the retro-contest people.
   + `log.csv`: This is just a recording of the time elapsed for every
     1000 steps. It should give you an idea of how fast your
     agent is running.
   + `monitor.csv`: Every row represents a trial the evaluation
     performed. The column `r` is the _reward_ for that trial, `l` is
     the number of steps it took to complete the trial, and `t` is the
     wall-clock time it took to complete the trial. This file can be
     automatically
     [analyzed](https://gitlab.com/sAnIc-ND/sAnIc#analyze-results).
   + `bk2` is a directory containing visual information for each trial
     that can
     be
     [converted into `.mp4` videos](https://gitlab.com/sAnIc-ND/sAnIc#convert-bk2-files-to-mp4-videos). Due
     to the nature of Docker, this file is recursively owned by
     `root`, so manipulating or removing this file will require root
     permissions, but there is nothing inherently root-worthy in this
     directory.

### Analyze Results ###
`local_eval.py` and `$ ./whateveragent.py --monitor` produce a file
called `monitor.csv` (see step
5 [here](https://gitlab.com/sAnIc-ND/sAnIc#simulate-an-agent-locally)
for full details). This file is the key to statistical and graphical
analysis. Run `$ analyze_monitor.py monitor_path "Title of
Experiment"` to produce analytical output. This will leave four files
in the directory containing `monitor_path`.
+ `stats.json`: Obviously this is a serialized JSON object. In it you
  will find descriptive statistics like mean, median, stddev,
  etc. regarding rewards and timestep lengths. This can be ingested
  with
  [`json.load()`](https://docs.python.org/3.6/library/json.html?highlight=json#json.load).
+ `rewards.svg`: This is an `svg` depicting two super-imposed plots: a
  scatter plot of the rewards of every episode, and a line plot of the
  mean reward at any given timestep. This can be opened in a web
  browser.
+ `histogram.svg`: This is a 10-bin histogram of all rewards. This can
  be opened in a web browser.
+ `analysis.html`: This is a webpage displaying the experiment title,
  `stats.json` as a table, `rewards.svg`, and `histogram.svg`.

### Evaluate an Agent On Many Tests ###
Evaluating an agent
on
[one game locally](https://gitlab.com/sAnIc-ND/sAnIc#simulate-an-agent-locally) can
be great for debugging, but it's not really what we need for
analytics. In the classic data science framework we need to run our
agents on test sets, and here's how.
1. Run `$ test_agent.py [--path PATH] [--results_dir RESULTS_DIR] [--nprocs NPROCS] tests_file timestep_limit name version`.
   Every line of the `tests_file` is an environment to test the agent
   in; a game title followed by a state name, separated by white space
   (here's
   [an example](https://gitlab.com/sAnIc-ND/sAnIc/blob/master/agents/example/example.tests)). The
   `timestep_limit` specifies the timestep limit for each
   environment. The `--nprocs` flag allows us to perform these
   experiments in parallel! And `--path` can be used if a Docker
   container needs to be built.
2. This will output a folder named `results` (can override with
   `--results_dir`). This is similar to singular, local evaluation
   results, but inside this directory is many more directories. Each
   subdirectory holds the output of the experiment corresponding to
   the subdirectory name.

### Analyze a Batch of Results ###
The first thing you might want to do is merge many `monitor.csv` files
into a single, large `monitor.csv` file. For example, if you ran 30
trials of an agent on the same level with the same parameters, then
you are probably interested in the aggregate performance of this agent
and not interested in the trials individually. To do this run `$
merge_monitors.py path1 path2...` where `pathX` is a path to some
`monitor.csv`. By default the result is printed, but the `-o` flag can
be used to designate an output filename. The actual merge process is
too complicated for this document, but the output has the properties
of a **single** agent performing _all_ of the actions that the
constituent agents performed.

Much like analyzing
a
[single result](https://gitlab.com/sAnIc-ND/sAnIc#analyze-results),
analyzing a batch of `monitor.csv` files is done with a script,
`compare_monitors.py`. Run `$ compare_monitors.py output_dir comparison_name name1 path1 name2 path2...`
to produce results. The arguments are as follows
* `output_dir`: Location where results will be stored.
* `comparison_name`: Used to title the figures and pages generated. It
  should characterize the intent behind comparing these results.
* `name1 path1 name2 path2...`: This is a list of experiment names and
  their corresponding `monitor.csv`s. The experiment names should
  characterize the data in their `monitor.csv` in the context of the
  comparison. These names will be used for legend labels in the
  figures and pages generated.

This will produce a `histogram.svg`, `rewards.svg`, and
`analysis.html` in `output_dir` that correspond to their single result
counterparts, but compiles the data from all of the `monitor.csv`s
under consideration.

### Submit a Job ###
The leaderboard only ranks the _most recent_ result for your team, so
this should only be done after careful testing and analysis. Ask
Conrad to help you take an agent through these stages.

### Convert `.bk2` Files to `.mp4` Videos ###
These steps require the `ffmpeg` application with `x264` support.
1. Make sure the `.bk2` file is **not** owned by `root`. This can be
   done to
   `local_eval.sh`
   [produced results](https://gitlab.com/sAnIc-ND/sAnIc#simulate-an-agent-locally) with
   `$ sudo chown -R username:username results/bk2` (this is an
   example, your invocation may vary).
2. Activate your virtual environment (see step
   3
   [here](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)).
3. To **store** the output use
   `$ python3 -m retro.scripts.playback_movie somefile.bk2`.
   This will produce `somefile.mp4` in the working directory. To
   **immediately view** the output use
   `python3 -m retro.scripts.playback_movie somefile.bk2 -v viewer` where
   `viewer` is the name of the application you'd like to use to view
   the movie (e.g. `vlc`, `mplayer`, etc).

### Resources ###
#### Contest Websites ####
+ [Poster/Front Page](https://contest.openai.com/): The basics of the contest.
+ [Blog Post](https://blog.openai.com/retro-contest/): Some details
  about the work they've already put in and their hopes for the
  contest.
+ [Details Page](https://contest.openai.com/details): Digs into the
  meat of the contest and the tools that they provide.
+ [Leaderboard](https://contest.openai.com/leaderboard): The current,
  live contest results.
+ [Benchmark Whitepaper](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/retro-contest/gotta_learn_fast_report.pdf):
  This is an academic paper describing the benchmark they use for
  measuring performance.
+ [Discord Server](https://discord.gg/chU7Zwa): Go here to reach out
  to the community and admins for questions or the Troubleshooting
  channel. In my experience they're very helpful, as long as it's not
  the weekend.

#### Repositories ####
**NOTE**: Visit these links and peruse the READMEs; they often have
very valuable information.
+ [Gym](https://github.com/openai/gym): A toolkit for developing and
  comparing reinforcement learning algorithms. This is the kernel of
  the contest.
+ [Gym Retro](https://github.com/openai/retro): The foundation of the
  contest. This turns emulators into Gym environments. It's what
  allows us to interact with the Sega Genesis video games.
+ [Retro-Contest](https://github.com/openai/retro-contest):
  Contest-specific wrappers for Gym-Retro and various support tools.
+ [Retro-Baselines](https://github.com/openai/retro-baselines):
  Contest entry examples that the OpenAI team has pre-built. You can
  try these out for yourself with a little modification.

#### Learning ####
+ [Neural Networks and Deep Learning](http://neuralnetworksanddeeplearning.com/):
  This online "book" gives the basics of neural networks. It's a
  pretty quick, approachable read.
+ [MIT 6.S094: Deep Learning for Self-Driving Cars](https://selfdrivingcars.mit.edu/):
  Check out the _Schedule of Lectures and Talks_ section. Most
  lectures begin with an hour of machine learning theory, and then end
  with applications specific to autonomous driving. Also check out
  their [resources](https://selfdrivingcars.mit.edu/resources/) page.
