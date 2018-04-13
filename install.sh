#!/bin/sh

PROG_NAME=$(basename "$0")
USAGE="Usage: $PROG_NAME [ROM Directory]"

# Constants #
PYTHON=python3
PIP=pip3

REQUIRED_BINS="$PIP $PYTHON grep virtualenv git"
REQUIRED_PIP_PKGS="https://storage.googleapis.com/gym-retro/builds/gym_retro-0.5.3-cp36-cp36m-linux_x86_64.whl"
REQUIRED_GAMES="SonicTheHedgehog-Genesis SonicTheHedgehog2-Genesis SonicAndKnuckles3-Genesis"

# Validate Input #
printf '%s' "Testing dir argument..."
if [ $# -ne 1 ] ; then
		printf '\n%s\n%s\n' "ERROR: Invalid number of arguments" "$USAGE" 1>&2
		exit 1
fi
echo "good"

ROM_DIR="$1"

printf '%s' "Testing dir existence..."
if [ ! -e "$ROM_DIR" ] ; then
		printf '\n%s\n' "ERROR: path '$ROM_DIR' does not exist" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing dir directory..."
if [ ! -d "$ROM_DIR" ] ; then
		printf '\n%s\n' "ERROR: path '$ROM_DIR' is not a directory" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing dir permissions..."
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

## glibc ##
LIBC=$(ldd --version | head -n1 | awk -F'[()]' '{print $2}')
printf '%s' "Testing ldd exit status..."
if [ $? -ne 0 ] ; then
		printf '\n%s\n' "ERROR: problem executing ldd" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing glibc existence..."
if [ "$LIBC" != "GNU libc" ] ; then
		printf '\n%s\n' "ERROR: GNU libc $GLIBC_REQUIRED_VERSION is required" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing ldd exit status..."
GLIBC_REQUIRED_VERSION=214
GLIBC_VERSION=$(ldd --version | head -n1 | sed 's/ /\n/g' | tail -1 | tr -d .)
if [ $? -ne 0 ] ; then
		printf '\n%s\n' "ERROR: problem executing ldd" 1>&2
		exit 1
fi
echo "good"

printf '%s' "Testing glibc version..."
if [ $GLIBC_VERSION -lt $GLIBC_REQUIRED_VERSION ] ; then
		printf '\n%s\n' "ERROR: GNU libc $GLIBC_REQUIRED_VERSION is required" 1>&2
		exit 1
fi
echo "good"

# Setup Virtual Environment #
printf '%s' "Making venv..."
OUTPUT=$(virtualenv -p"$PYTHON" 2>&1 venv)
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '\n%s\n%s\n' "ERROR: Problem creating virtual environment with virtualenv" "$OUTPUT" 1>&2
		exit $STATUS
fi
echo "good"

printf '%s' "Activating venv..."
. venv/bin/activate
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '\n%s\n%s\n' "ERROR: Problem activating virtual environment with '. venv/bin/activate'" "$OUTPUT" 1>&2
		exit $STATUS
fi
echo "good"

## Retrieve Contest Version of Gym ##
printf '%s' "Cloning contest repo..."
OUTPUT=$(git clone -q --recursive https://github.com/openai/retro-contest.git)
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '%s\n%s\n' "ERROR: problem cloning contest repository. Propagating exit status." "$OUTPUT" 1>&2
		exit $STATUS
fi
echo "good"

## Pip Install Contest Version of Gym ##
printf '%s' "Installing contest pip package..."
OUTPUT=$("$PIP" install -e 'retro-contest/support[docker]')
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '%s\n%s\n' "ERROR: problem installing contest Gym with pip. Propagating exit status." "$OUTPUT" 1>&2
		exit $STATUS
fi
echo "good"

## Pip Install Non-Local Packages ##
for PKG in $REQUIRED_PIP_PKGS ; do
		printf '%s' "Installing pip pkg $PKG..."
		OUTPUT=$("$PIP" install "$PKG" 2>&1)
		STATUS=$?
		if [ $STATUS -ne 0 ] ; then
				printf '\n%s\n%s\n' "ERROR: Something went wrong while installing package '$PKG' in virtual environment. Propagating exit status." "$OUTPUT" 1>&2
				exit $STATUS
		fi
		echo "good"
done


# Install ROMs into Retro Gym #
printf '%s' "Importing games..."
OUTPUT=$("$PYTHON" -m retro.import "$ROM_DIR")
echo "good"

for GAME in $REQUIRED_GAMES ; do
		printf '%s' "Finding game $GAME..."
		if [ $(echo "$OUTPUT" | grep -c "$GAME") -eq 0 ] ; then
				printf '\n  %s\n' "WARNING: Did not find '$GAME' in ROM directory '$ROM_DIR'" 1>&2
		else
				echo "good"
		fi
done

exit 0

