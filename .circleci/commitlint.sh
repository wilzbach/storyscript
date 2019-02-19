#!/usr/bin/env bash

set -euo pipefail

if [ -n "${CIRCLE_PULL_REQUEST}" ]
then
  git remote add upstream "https://github.com/storyscript/storyscript.git"
  # Fetch GitHub's automatic PR branch (the PR branch is merged into the target branch)
  git fetch -q upstream "+refs/pull/${CIRCLE_PR_NUMBER}/merge:"
  git checkout -f FETCH_HEAD
  # We display the parent commits of the merge commit
  COMMIT_RANGE="$(git show --pretty='%P' | sed 's/ /.../')"
  git checkout -
  echo "Commit range: ${COMMIT_RANGE}"
  git log "${COMMIT_RANGE}" --pretty=%B | npx commitlint
else
  echo "We only lint pull requests"
fi
