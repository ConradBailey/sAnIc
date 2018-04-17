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
* pip3
* virtualenv
* git
* glibc 2.14
* docker

#### Requirements ####
* 64-bit Architecture

## How To Do Stuff Relevant To This Project ##
### Table of Contents ###
* [Assumptions](https://gitlab.com/sAnIc-ND/sAnIc#assumptions)
* [Install the Virtual Environment](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)
* [Contribute to the Project](https://gitlab.com/sAnIc-ND/sAnIc#contribute-to-the-project)
* [Work on the Website](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)
* [Start a Jupyter Notebook in the Virtualenv](https://gitlab.com/sAnIc-ND/sAnIc#start-a-jupyter-notebook-in-the-virtualenv)
* [Evaluate an Agent Locally](https://gitlab.com/sAnIc-ND/sAnIc#evaluate-an-agent-locally)
* [Submit a Job](https://gitlab.com/sAnIc-ND/sAnIc#submit-a-job)
* [Convert `.bk2` Files to `.mp4` Videos](https://gitlab.com/sAnIc-ND/sAnIc#convert-bk2-files-to-mp4-videos)

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
  or `pip2`; _use `pip3`_* just to be explicitly compliant. Use
  `#!/usr/bin/env python3` for your shebangs.
* You've installed the dependencies yourself. You need how to
  figure this out for your own environment, e.g. Ubuntu will need
  calls to `$ sudo apt-get install` or something.

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
   your shell prompt. That means anything installed with `pip3` will
   be local to this virtualenv and can be cleanly swept away with `rm
   -r venv`. To get out of this environment when you're done working
   on the project run `deactivate`, it's that simple.

### Contribute to the Project ###
Things can get really messy with dependencies and outside libraries
and everything else. For that reason we will use pull requests to
contribute work instead of straight pushes to the repo.
1. [Fork](https://docs.gitlab.com/ee/gitlab-basics/fork-project.html) the
   project from the group repo.
2. You should
   probably
   [make a branch](https://www.atlassian.com/git/tutorials/using-branches) to
   do your work in.
3. Do whatever work you want to do. Make an agent with a new
   algorithm. Do new visualizations or analytics for an old
   agent. [Work on the website](https://gitlab.com/sAnIc-ND/sAnIc#work-on-the-website). Whatever!
3. Make sure you've committed everything you want and push the branch
   to your own forked repo,
   then
   [create a merge request](https://docs.gitlab.com/ee/gitlab-basics/add-merge-request.html) with
   the main repo. The group can review your changes and merge them
   when they're ready. We're messing with large amounts of data,
   sensitive data, large files, and a somewhat complicated dev
   environment, so this is a necessary sanity check.

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

### Evaluate an Agent Locally ###
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
3. Write a Docker file for your agent. See examples and Docker
   documentation. They're really not bad; waaayyy easier than
   makefiles.
4. Run `$ local_eval.sh [Docker File] [Agent Name] [Agent Version] [Game Name] [State Name] [Time Limit (secs)]`.
   This will build a docker image tagged as
   `$TEAM_MEMBER_NAME/$AGENT_NAME:v$AGENT_VERSION`, pull the
   `retro-env` image, tag `retro-env` as `remote-env`, and run a local
   evaluation with `$ retro-contest run` using the new docker image
   for the agent and the specified game and state for the
   environment. The time limit determines how long the agent is
   evaluated for in wall-clock time; i.e. it will run as many trials
   of that game and state as it can before the allotted time runs out.
5. This will output a folder named `results` in the working
   directory. In this directory there are useful files:
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
     wall-clock time it took to complete the trial.
   + `bk2` is a directory containing visual information for each trial
     that can
     be
     [converted into `.mp4` videos](https://gitlab.com/sAnIc-ND/sAnIc#convert-bk2-files-to-mp4-videos). Due
     to the nature of Docker, this file is recursively owned by
     `root`, so manipulating or removing this file will require root
     permissions, but there is nothing inherently root-worthy in this
     directory.

### Submit a Job ###
Submitting a job means packaging some agent up in a Docker container
and asking the retro-contest server to officially evaluate it for the
contest. The simplest agents take around an hour to finish
evaluations. Furthermore, we can only run one of these at a time, so
communicate your intentions to the group for scheduling purposes. If
your agent beats our high score, then its performance becomes our new
high score!
1. [Evaluate your agent locally](https://gitlab.com/sAnIc-ND/sAnIc#evaluate-an-agent-locally). This
   ensures there are no runtime bugs and you don't waste resources
   uploading doomed agents to be evaluated. I'm still working on
   automating this part, but there will be an _Evaluate Locally_
   section here soon.
2. Run `$ ./submit_agent.sh docker_file agent_name agent_version`
   where `agent_name` should describe the implementation and
   `agent_version` allows you to iterate on that implementation. This
   script will build the Docker container for your agent, tag it as
   `$TEAM_MEMBER_NAME/$AGENT_NAME:v$AGENT_VERSION`, and submit it for
   evaluation. You shouldn't have to worry about these details, but
   this info is helpful if you're managing your Docker images.
3. You can check or change the status of your job at
   the [jobs page](https://contest.openai.com/user/job).

### Convert `.bk2` Files to `.mp4` Videos ###
These steps require the `ffmpeg` application with `x264` support.
1. Make sure the `.bk2` file is **not** owned by `root`. This can be
   done to
   `local_eval.sh`
   [produced results](https://gitlab.com/sAnIc-ND/sAnIc#evaluate-an-agent-locally) with
   `$ sudo chown -R username:username results/bk2` (this is an
   example, your invocation may vary).
2. Activate your virtual environment (see step
   3
   [here](https://gitlab.com/sAnIc-ND/sAnIc#install-the-virtual-environment)).
3. To **store** the output use
   `$ python3 -m retro.scripts.playback_movie somefile.bk2`.
   This will produce `somefile.mp4` in the working directory. To
   **immediately view** the output use
   `python3 -m retro.scripts.playback_movie -v viewer` where
   `viewer` is the name of the application you'd like to use to view
   the movie (e.g. `vlc`, `mplayer`, etc).
