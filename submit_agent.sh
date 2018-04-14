#!/bin/sh

get_abs_location() {
		cd "$(dirname "$1")" || exit 1
		pwd
		exit 0
}

PROG_NAME=$(basename "$0")
USAGE="Usage: $PROG_NAME [Docker File] [Agent Name] [Agent Version]"

# Validate Arguments #
if [ $# -ne 3 ] ; then
		printf '\n%s\n%s\n' "ERROR: Invalid number of arguments" "$USAGE" 1>&2
		exit 1
fi
DOCKER_FILE="$1"
AGENT_NAME="$2"
AGENT_VERSION="$3"

# Required Files #
TOP_LEVEL_DIR=$(get_abs_location "$0")
if [ $? -ne 0 ] ; then
		printf '%s\n' "ERROR: Could not establish absolute path for executable" 1>&2
		exit 1
fi

CREDENTIALS_FILE="$TOP_LEVEL_DIR/retro_contest_credentials.dontcommit"
VENV_ACTIVATION_FILE="$TOP_LEVEL_DIR/venv/bin/activate"

REQUIRED_FILES="$CREDENTIALS_FILE $DOCKER_FILE $VENV_ACTIVATION_FILE"

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
		if [ -z $(which "$BIN" 2>/dev/null) ] ; then
				printf '\n%s\n' "ERROR: $BIN not in path" 1>&2
				exit 1
		fi
done

# Check Credentials #
REQUIRED_CREDENTIALS="DOCKER_REGISTRY_URL TEAM_EMAIL_ADDR TEAM_PASSWORD TEAM_MEMBER_NAME"
for CRED in  $REQUIRED_CREDENTIALS ; do
		if [ $(grep -c "$CRED" "$CREDENTIALS_FILE") -eq 0 ] ; then
				printf '%s\n' "ERROR: credentials file is missing requirement '$CRED'" 1>&2
				exit 1
		fi
done

# Docker Operations #
DOCKER_TAG="$TEAM_MEMBER_NAME/$AGENT_NAME:v$AGENT_VERSION"
## Build ##
printf '%s' "Docker: Building image..."
OUTPUT=$(docker build -f "$DOCKER_FILE" -t "$DOCKER_TAG" . 2>&1)
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '\n%s\n%s\n' "ERROR: Problem building Docker image. Propagating exit status." "$OUTPUT" 1>&2
		exit $STATUS
fi
printf '%s\n' "good"


# Server Operations #
## Login ##
printf '%s' "Server: Logging in..."
OUTPUT=$(retro-contest login --server 'https://contest.openai.com' --email "$TEAM_EMAIL_ADDR" --password "$TEAM_PASSWORD" 2>&1)
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '\n%s\n%s\n' "ERROR: Problem logging into server. Propagating exit status." "$OUTPUT" 1>&2
		exit $STATUS
fi
printf '%s\n' "good"

## Submit ##
printf '%s' "Server: Submitting job..."
OUTPUT=$(retro-contest job submit -t "$DOCKER_TAG" 2>&1)
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '\n%s\n%s\n' "ERROR: Problem submitting job for '$AGENT_NAME:$AGENT_VERSION'. Propagating exit status." "$OUTPUT" 1>&2
		exit $STATUS
fi
printf '%s\n' "good"

## Logout ##
printf '%s' "Server: Logging out..."
OUTPUT=$(retro-contest logout 2>&1)
STATUS=$?
if [ $STATUS -ne 0 ] ; then
		printf '\n%s\n%s\n' "ERROR: Problem logging out of server. Propagating exit status." "$OUTPUT" 1>&2
		exit $STATUS
fi
printf '%s\n' "good"

exit 0
