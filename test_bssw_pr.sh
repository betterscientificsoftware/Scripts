#!/usr/bin/env bash

# Normal Colors
NC="\033[0m"              # Color Reset
Black="\033[0;30m"        # Black
Red="\033[0;31m"          # Red
Green="\033[0;32m"        # Green
Brown="\033[0;33m"        # Brown
Blue="\033[0;34m"         # Blue
Purple="\033[0;35m"       # Purple
Cyan="\033[0;36m"         # Cyan
LtGray="\033[0;37m"       # LtGray

BRed="\033[1;31m"         # Bright Red
BGreen="\033[1;32m"       # Bright Green
Yellow="\033[1;33m"       # Yellow
BBlue="\033[1;34m"        # Bright Blue
BPurple="\033[1;35m"      # Bright Purple
BCyan="\033[1;36m"        # Bright Cyan
White="\033[1;37m"        # White

echo -e "${Cyan}--------------------------------------------------------------------------------${NC}"
echo -e "${Cyan}- ${Yellow}BSSw Pull Request Test${NC}"
echo -e "${Cyan}--------------------------------------------------------------------------------${NC}"

echo -e "${Cyan}----------------------------------------${NC}"
echo -e "${Cyan}- ${Yellow}env vars${NC}"
echo -e "${Cyan}----------------------------------------${NC}"
echo -e "TRAVIS                     = ${TRAVIS}"
echo -e "TRAVIS_BRANCH              = ${TRAVIS_BRANCH}"
echo -e "TRAVIS_COMMIT              = ${TRAVIS_COMMIT}"
echo -e "TRAVIS_EVENT_TYPE          = ${TRAVIS_EVENT_TYPE}"
echo -e "TRAVIS_PULL_REQUEST        = ${TRAVIS_PULL_REQUEST}"
echo -e "TRAVIS_PULL_REQUEST_BRANCH = ${TRAVIS_PULL_REQUEST_BRANCH}"
echo -e "TRAVIS_PULL_REQUEST_SHA    = ${TRAVIS_PULL_REQUEST_SHA}"
echo -e "TRAVIS_PULL_REQUEST_SLUG   = ${TRAVIS_PULL_REQUEST_SLUG}"
echo -e "TRAVIS_COMMIT_RANGE        = ${TRAVIS_COMMIT_RANGE}"
echo -e "TRAVIS_BUILD_DIR           = ${TRAVIS_BUILD_DIR}"
pwd

if [ ! -n  "${TRAVIS}" ]; then
    echo ""
    echo -e "${Red}ERROR  ${NC}:  Travis-CR Not Found"
    echo ""
    exit 1
fi

if [ ! ${TRAVIS_PULL_REQUEST} == false ]; then
    echo -e "${Yellow}MESSAGE${NC}:  Not a Pull Request"
    # exit 0
fi

if [[ "${TRAVIS_COMMIT_RANGE}" == "" ]]; then
    echo -e "${Yellow}MESSAGE${NC}:  No changes detected"
    exit 0
fi

# Get the list of changed files.
git diff --name-only ${TRAVIS_COMMIT_RANGE} > ${TRAVIS_BUILD_DIR}/___git_changes.txt
# git status --name-status ${TRAVIS_COMMIT_RANGE} > ${TRAVIS_BUILD_DIR}/___git_changes.txt

cd ${TRAVIS_BUILD_DIR}

# Execute the PR test.
___Scripts/test_article_metadata/validate_gitdiff_statfile.py \
  -s ___Scripts/test_article_metadata/config-metadata.txt     \
  -p ___Scripts/test_article_metadata/config-package-list.csv \
  -f ___git_changes.txt \
  --color=tty \
  -V
ierror=$?

if [[ $ierror != 0 ]]; then
    echo -e "${Red}ERROR  ${NC}:  Something failed"
    exit $ierror
fi

