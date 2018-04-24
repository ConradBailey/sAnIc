#!/bin/sh

safe_run() {
		DESCRIPTION="$1"
		COMMAND="$2"
		ERR_MSG="$3"
		printf '%s' "$DESCRIPTION..."
		OUTPUT=$($COMMAND 2>&1)
		STATUS=$?
		if [ $STATUS -ne 0 ] ; then
				printf '\n%s\n%s\n' "ERROR: $ERR_MSG Propagating exit status." "$OUTPUT" 1>&2
				exit $STATUS
		fi
		echo "good"
}

PROG_NAME=$(basename "$0")
USAGE="Usage: $PROG_NAME [ROM Directory]"

# Constants #
PYTHON=python3.6
PIP=pip3.6

REQUIRED_BINS="$PIP $PYTHON grep virtualenv git"
REQUIRED_PIP_PKGS="gym-retro \
                   ipykernel \
									 numpy \
									 pandas \
									 matplotlib \
									"

REQUIRED_GAMES="SonicTheHedgehog-Genesis SonicTheHedgehog2-Genesis SonicAndKnuckles3-Genesis"

# Validate Input #
if [ $# -ne 1 ] ; then
		printf '\n%s\n%s\n' "ERROR: Invalid number of arguments" "$USAGE" 1>&2
		exit 1
fi

ROM_DIR="$1"

printf '%s' "Testing '$ROM_DIR' existence..."
if [ ! -e "$ROM_DIR" ] ; then
		printf '\n%s\n' "ERROR: path '$ROM_DIR' does not exist" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing '$ROM_DIR' directory..."
if [ ! -d "$ROM_DIR" ] ; then
		printf '\n%s\n' "ERROR: path '$ROM_DIR' is not a directory" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing '$ROM_DIR' permissions..."
if [ ! -r "$ROM_DIR" ] || [ ! -x "$ROM_DIR" ] ; then
		printf '\n%s\n' "ERROR: path '$ROM_DIR' does not have correct permissions" 1>&2
		exit 1
fi
echo "good"

# Gym Retro requires 64-bit architecture
printf '%s' "Testing architecture..."
if [ "$(uname -m)" != "x86_64" ] ; then
		printf '\n%s\n' "ERROR: only x86_64 is supported" 1>&2
		exit 1
fi
echo "good"


# Required Binaries
for BIN in $REQUIRED_BINS ; do
		printf '%s' "Testing $BIN..."
		if [ -z $(which "$BIN" 2>/dev/null) ] ; then
				printf '\n%s\n' "ERROR: $BIN not in path" 1>&2
				exit 1
		fi
		echo "good"
done


# Required Versions #
## Python ##
PYTHON_REQUIRED_VERSION=360
PYTHON_VERSION=$("$PYTHON" --version | cut -f2 -d' ' | tr -d .)
printf '%s' "Testing python version exit status..."
if [ $? -ne 0 ] ; then
		printf '\n%s\n' "ERROR: problem executing python --version" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing python version..."
if [ $PYTHON_VERSION -lt $PYTHON_REQUIRED_VERSION ] ; then
		printf '\n%s\n' "ERROR: $PYTHON must be of version $PYTHON_REQUIRED_VERSION" 1>&2
		exit 1
fi
echo "good"

# Setup Virtual Environment #
if [ -e 'venv' ] ; then
		read -p "'venv' exists. Would you like to remove and reinstall 'venv' (y/n)? " ANSWER
		case "$ANSWER" in
				'y') safe_run "Removing pre-existing 'venv'" "rm -rf venv" "problem removing existing 'venv'";;
				*) printf '%s\n' "Using 'venv' as is"
		esac
fi

if [ ! -e 'venv' ] ; then
		safe_run "Making venv" "virtualenv -p$PYTHON venv" "Problem creating virtual environment with virtualenv"
fi

printf '%s' "Activating venv..."
. venv/bin/activate
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '\n%s\n%s\n' "ERROR: Problem activating virtual environment with '. venv/bin/activate'" "$OUTPUT" 1>&2
		exit $STATUS
fi
echo "good"

## Pip Install Non-Local Packages ##
for PKG in $REQUIRED_PIP_PKGS ; do
		safe_run "Installing pip pkg $PKG" "$PIP install $PKG" "Something went wrong while installing package '$PKG' in virtual environment. Propagating exit status."
done

## Install retro-contest ##
if [ -e "retro-contest" ] ; then
		### Update repo ###
		if [ ! -d "retro-contest/.git" ] ; then
				printf '%s\n' 'ERROR: "retro-contest" exists, but is not a git repo.'
				exit 1
		fi
		safe_run 'Directory "retro-contest" exists and is a git repository. Pulling updates' "cd retro-contest && git pull 2>&1" "problem pulling updates in 'retro-contest'."
else
		### Retrieve retro-contest ###
		safe_run "Cloning contest repo" "git clone -q --recursive https://github.com/openai/retro-contest.git" "problem cloning contest repository."
fi

### Pip Install retro-contest ###
safe_run "Installing retro-contest pip package" "$PIP install -e retro-contest/support[docker,rest,retro]" "problem installing retro-contest pip package."

# Install ROMs into Retro Gym #
safe_run "Importing games" "$PYTHON -m retro.import $ROM_DIR" "problem importing games from $ROM_DIR"

for GAME in $REQUIRED_GAMES ; do
		printf '%s' "Finding game $GAME..."
		if [ $(echo "$OUTPUT" | grep -c "$GAME") -eq 0 ] ; then
				printf '\n  %s\n' "WARNING: Did not find '$GAME' in ROM directory '$ROM_DIR'" 1>&2
		else
				echo "good"
		fi
done

exit 0

