#!/bin/bash

set -e

# Install `asdf` to manage most tooling installation
# https://asdf-vm.com/guide/getting-started.html#_1-install-dependencies
test -d ~/.asdf || git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.10.0

# Add this to your .bashrc if you want to use `asdf`
. $HOME/.asdf/asdf.sh
. $HOME/.asdf/completions/asdf.bash

# Install plugins
asdf plugin add helm || true
asdf plugin add kind || true
asdf plugin add kubectl || true

# Install project versions
asdf install

# Show installed versions
asdf current

# Also promt user to install argo, not managed by `asdf`
which argo && argo version || { echo; echo; echo "[REQUIRED] Install argo manually: https://github.com/argoproj/argo-workflows/releases/tag/v3.3.6"; exit 1; }