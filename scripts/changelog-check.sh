#!/bin/bash

set +x

if [[ -z "$CI" ]]; then
   echo "This script is intended to be run only on Github Actions." >&2
   exit 1
fi

CHANGELOG_PATH='changelogs/unreleased'

# https://help.github.com/en/actions/reference/events-that-trigger-workflows#pull-request-event-pull_request
# GITHUB_REF is something like "refs/pull/:prNumber/merge"
pr_number=$(echo $GITHUB_REF | cut -d / -f 3)

change_log_file="${CHANGELOG_PATH}/${pr_number}-*"

if ls ${change_log_file} 1> /dev/null 2>&1; then
    echo "changelog for PR ${pr_number} exists"
    exit 0
else
    echo "PR ${pr_number} is missing a changelog. Please add a changelog."
    exit 1
fi