# Cody's dotfiles

The purpose of this repository is to provide my development environment as code.

## Setup

To install dependencies and setup your home directory for the first time, run:

```
./setup.sh
```

## Sync from dotfiles repo to $HOME

To update your home directory with the latest changes from this repository, run:

```
./bin/sync.py
```

## Coding

ALWAYS edit files in this repository under version control. Then sync them to your home directory using the command above (ideally after sourcing/running in a shell and testing first).

DO NOT sync on behalf of the user.
