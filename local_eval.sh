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

get_abs_location() {
		cd "$(dirname "$1")" || exit 1
		pwd
		exit 0
}

PROG_NAME=$(basename "$0")
USAGE="Usage: $PROG_NAME [Docker File] [Agent Name] [Agent Version] [Game Name] [State Name] [Time Step Limit]"

# Validate Arguments #
if [ $# -ne 6 ] ; then
		printf '\n%s\n%s\n' "ERROR: Invalid number of arguments" "$USAGE" 1>&2
		exit 1
fi
DOCKER_FILE="$1"
AGENT_NAME="$2"
AGENT_VERSION="$3"
GAME_NAME="$4"
STATE_NAME="$5"
TIME_LIMIT="$6"

# Required Files #
TOP_LEVEL_DIR=$(get_abs_location "$0")
if [ $? -ne 0 ] ; then
		printf '%s\n' "ERROR: Could not establish absolute path for executable" 1>&2
		exit 1
fi

CREDENTIALS_FILE="$TOP_LEVEL_DIR/retro_contest_credentials.dontcommit"
VENV_ACTIVATION_FILE="$TOP_LEVEL_DIR/venv/bin/activate"
GAME_STATES_LIST="$TOP_LEVEL_DIR/game_states.txt"
GAME_ROM="$TOP_LEVEL_DIR/venv/lib/python3.6/site-packages/retro/data/$GAME_NAME/rom.md"

REQUIRED_FILES="$CREDENTIALS_FILE $DOCKER_FILE $VENV_ACTIVATION_FILE $GAME_STATES_LIST $GAME_ROM"

for FILENAME in $REQUIRED_FILES ; do
		if [ ! -e "$FILENAME" ] ; then
				printf '%s\n' "ERROR: '$FILENAME' does not exist" 1>&2
				exit 1
		fi
		if [ ! -e "$FILENAME" ] ; then
				printf '%s\n' "ERROR: '$FILENAME' is not a file" 1>&2
				exit 1
		fi
		if [ ! -r "$FILENAME" ] ; then
				printf '%s\n' "ERROR: '$FILENAME' is not readable" 1>&2
				exit 1
		fi
done
## Import Sources ##
. "$CREDENTIALS_FILE"
. "$VENV_ACTIVATION_FILE"


# Required Binaries #
REQUIRED_BINS="docker retro-contest"
for BIN in $REQUIRED_BINS ; do
		if ! which "$BIN" 1>/dev/null 2>&1 ; then
				printf '\n%s\n' "ERROR: $BIN not in path" 1>&2
				exit 1
		fi
done

# Check Credentials #
REQUIRED_CREDENTIALS="TEAM_MEMBER_NAME"
for CRED in  $REQUIRED_CREDENTIALS ; do
		if ! grep -q "$CRED" "$CREDENTIALS_FILE" ; then
				printf '%s\n' "ERROR: credentials file is missing requirement '$CRED'" 1>&2
				exit 1
		fi
done

# Check for game state existence #
if ! grep -q "$GAME_NAME.*$STATE_NAME" "$GAME_STATES_LIST" ; then
		printf '%s\n' "ERROR: State '$STATE_NAME' is not a valid state of game '$GAME_NAME'" 1>&2
		exit 1
fi

# Docker Operations #
DOCKER_TAG="$TEAM_MEMBER_NAME/$AGENT_NAME:v$AGENT_VERSION"
## Build Image ##
safe_run "Docker: Building image" "docker build -f $DOCKER_FILE -t $DOCKER_TAG ." "Problem building Docker image."

## Make Remote Env ##
safe_run "Docker: Pulling retro-env" "docker pull openai/retro-env" "Problem pulling openai/retro-env."

## Tag Remote Env ##
safe_run "Docker: Tagging retro-env as remote-env" "docker tag openai/retro-env remote-env" "Problem tagging openai/retro-env as remote-env."

# Run Evaluations #
safe_run "Eval: Running evaluation" "retro-contest run --timestep-limit $TIME_LIMIT --agent $DOCKER_TAG --results-dir results --no-nv --use-host-data $GAME_NAME $STATE_NAME" "Problem running local evaluation."

exit 0
