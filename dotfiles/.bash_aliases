# Machine type detection
if [[ $(hostname) == *"ascend"* ]]; then
    export MACHINE_TYPE="WORK"
else
    export MACHINE_TYPE="LIFE"
fi

# Exports
## Path
export PATH="$HOME/.local/bin:$PATH"
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
export PATH="$HOME/go/bin:$PATH" # go stuff
export PATH="$HOME/.cargo/bin:$PATH" # rust stuff

## Editor
export EDITOR="nvim"
export VISUAL=nvim

## Python
export PYTHONBREAKPOINT="IPython.embed"
export PYTHONDONTWRITEBYTECODE=1
export OLLAMA_HOME="$HOME/.ollama"

## Locations
export AIO=$HOME/code/ascend-io
export DEV=$AIO/ascend-dev
export GHH=$HOME/code/lostmygithubaccount
export DKDC=$GHH/dkdc

## Homebrew
if [[ "$OSTYPE" == "darwin"* ]]; then
    export PATH="/opt/homebrew/bin:$PATH"
else
    export PATH="$HOME/.linuxbrew/bin:$PATH"
fi

## LS Colors
if [[ "$OSTYPE" == "darwin"* ]]; then
    export LSCOLORS=Gxfxcxdxbxegedabagacad
else
    export LS_COLORS="di=01;36:ln=01;36:so=01;35:pi=01;33:ex=01;32:bd=01;34:cd=01;34:su=30;41:sg=30;46:tw=30;42:ow=30;43"
fi

# Temporary helpers
function dct() {
  devcontainer up --dotfiles-repository https://github.com/lostmygithubaccount/dotfiles.git --workspace-folder . "$@"
}

function dcz() {
  devcontainer exec --workspace-folder . zsh "$@"
}

# Functions
## Config
function ali() {
  v $HOME/.bash_aliases
}

function update() {
    . $HOME/.zshrc
    git config --global core.excludesfile ~/.gitignore
}

function gitignore() {
  v $HOME/.gitignore
}

function vimrc() {
  v $HOME/.config/nvim/init.lua
}

function tmuxc() {
  v $HOME/.tmux.conf
}

function ipyrc() {
  v $HOME/.ipython/profile_default/ipython_config.py
}

function uvrc() {
  v $HOME/.config/uv/uv.toml
}

## Movement
function ascendio() {
  cd $HOME/code/ascend-io
}

function aio() {
  ascendio
}

function data() {
  cd $HOME/data
}

function profiles() {
  cd $HOME/profiles
}

function secrets() {
  cd $HOME/secrets
}

function vaults() {
    cd $HOME/vaults
}

function down() {
    cd $HOME/Downloads
}

function desk() {
    cd $HOME/Desktop
}

function docs() {
    cd $HOME/Documents
}

function d() {
    cd $DEV
}

function ghh() {
    cd $GHH
}

function websites () {
    cd $DKDC/websites
}

function dkdc.dev () {
    cd $DKDC/websites/dkdc.dev
}

function dkdc.io () {
    cd $DKDC/websites/dkdc.io
}

function dotfiles() {
    cd $DKDC/dotfiles
}

function files() {
  dkdc files "$@"
}

function p() {
  cd $AIO/product
}

function workspaces() {
  cd $DEV/workspaces
}

function ws() {
    workspaces
}

function pri() {
  dkdc files open pri.md
}

function todo() {
  if [[ "$MACHINE_TYPE" == "WORK" ]]; then
    dkdc files open work.md
  else
    dkdc files open life.md
  fi
}

function notes() {
  dkdc files open notes.md
}

## Core functionality
function e() {
    exit
}

function c() {
    clear
}

function cdesk() {
    rm -r $HOME/Desktop/*
}

function s() {
    duckdb "$@"
}

function todos () {
    grep -i "TODO" "$@"
}

function drafts () {
    grep ".*draft.*true.*" "$@"
}

function dc() {
  devcontainer "$@"
}

function v() {
  nvim "$@"
}

function vt() {
  v -c "T" "$@"
}

function m() {
  tmux "$@"
}

function r() {
  ranger "$@"
}

function links() {
  dkdc-links "$@"
}

function o() {
  links "$@"
}

function grep() {
  rg --hidden --glob "!public" --glob "!.env" --glob "!.git" --glob "!dist" --glob "!target" --glob "!ascend-out" "$@"
}

function g() {
  grep "$@"
}

function gi() {
  grep -i "$@"
}

function top() {
  btop "$@"
}

function du() {
  command du -h -d1 "$@" | sort -h
}

function loc() {
  scc "$@"
}

function find() {
  command find . -name "$@"
}

function f() {
  find "$@"
}

function glow() {
  command glow -p "$@"
}

function preview() {
    go-grip "$@"
}

function pr() {
    preview "$@"
}

function ..() {
  cd ..
}

function ...() {
  cd ../..
}

function ....() {
  cd ../../..
}

# quick mafs 
function l() {
  less "$@"
}

function tree() {
  command tree -F -I venv -I .git -I target -I dist -I target -I ascend-out "$@"
}

function t() {
  tree "$@"
}

function tl() {
  tree -L 1 "$@"
}

function tt() {
  tree -L 2 "$@"
}

function ttt() {
  tree -L 3 "$@"
}

function tttt() {
  tree -L 4 "$@"
}

function ls() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        command ls -1GhFA "$@"
    else
        command ls -1 --color=auto -hFA "$@"
    fi
}

function lsl() {
  ls -l "$@"
}

function fr() {
  if [ $# -ne 2 ]; then
    echo "Usage: fr <find_pattern> <replace_pattern>"
    return 1
  fi
  
  find_pattern="$1"
  replace_pattern="$2"
  
  # Check if we're on macOS (BSD sed) or Linux (GNU sed)
  if [[ "$(uname)" == "Darwin" ]]; then
    # macOS/BSD version - requires an extension for -i
    grep -l "$find_pattern" * 2>/dev/null | xargs -I{} sed -i '' "s/$find_pattern/$replace_pattern/g" {}
  else
    # Linux/GNU version
    grep -l "$find_pattern" * 2>/dev/null | xargs -I{} sed -i "s/$find_pattern/$replace_pattern/g" {}
  fi
  
  echo "Replaced \"$find_pattern\" with \"$replace_pattern\" in matching files"
}

### Remote commands
function rsync() {
  command rsync -av --exclude-from='.gitignore' "$@"
}

### Git commands
function gs() {
  git status "$@"
}

function gw() {
  git switch "$@"
}

function gn() {
  git switch -c "$@"
}

function gm() {
  git switch main
}

function gb() {
  git branch "$@"
}

function ga() {
  git add .
}

function gA() {
  git add -A
}

# lol
function cc() {
  git commit
}

function qs() {
  git add . && git commit -m 'qs'
}

function ss() {
  qs
}

function gc() {
  git commit -m "$@"
}

function gp() {
  git push "$@"
}

function gpf() {
  git push --force "$@"
}

function gl() {
  git log "$@"
}

function gr() {
  git rebase -i origin/main "$@"
}

function diff() {
  git diff --color-words --no-index "$@"
}

function ghpra() {
  gh pr list --state all "$@"
}

## AI
function ai() {
  # If only argument is -c, open CLAUDE.md in $EDITOR
  if [ "$#" -eq 1 ] && [ "$1" = "-c" ]; then
    ${EDITOR:-vim} "$HOME/AGENTS.md"
    return 0
  fi
  
  # Otherwise, pass all arguments to claude as before
  claude --dangerously-skip-permissions "$@"
}

function ai2() {
  codex --full-auto "$@"
}

## Miscellaneous
function temp() {
  v temp.md
}

function rand() {
    openssl rand -base64 32
}

function git400() {
  git config http.postBuffer 524288000
}

## Docker & Kubernetes
function cya (){
    docker rm -f $(docker ps -aq) 2>/dev/null && echo "All containers killed and removed" || echo "No containers found"
}

function kt() {
    kubectl "$@"
}

function kpr () 
{ 
    kubectl get pod -L ascend.io/runtime-id -L ascend.io/runtime-kind -L ascend.io/environment-id $@
}

function kpro () 
{ 
    kpr -n ottos-expeditions $@
}

## GitHub
function ghprc() {
  local repo="${1:-}"
  local pr_number="${2:-}"
  local org="ascend-io"

  # Derive missing arguments with gh
  if [[ -z "$repo" ]]; then
    repo=$(gh repo view --json name --jq '.name' 2>/dev/null) || repo=""
  fi
  if [[ -z "$pr_number" ]]; then
    pr_number=$(gh pr view --json number --jq '.number' 2>/dev/null) || pr_number=""
  fi

  # Validate
  if [[ -z "$repo" ]]; then
    echo "Error: repo not specified and could not determine current repository." >&2
    return 1
  fi
  if [[ -z "$pr_number" ]]; then
    echo "Error: PR number not specified and could not determine current pull request." >&2
    return 1
  fi

  gh api --paginate -H "Accept: application/vnd.github+json" \
        "/repos/${org}/${repo}/pulls/${pr_number}/comments" |
    jq -r '
      .[] |
      "Reviewer: \(.user.login)
File:     \(.path) (line \(.line // "N/A"))
Diff:
\(.diff_hunk)
Comment:
\(.body)
-------------------------------------------------------------------------------"
    '
}

function prit() {
    echo "# PR description\n" > pr.md
    gh pr view >> pr.md
    echo "# PR comments\n" >> pr.md
    gh pr view -c >> pr.md
    echo "# PR diff\n" >> pr.md
    gh pr diff >> pr.md
    echo "# PR review comments\n" >> pr.md
    ghprc >> pr.md
}

## Common typos
function dkcd() {
  dkdc "$@"
}

function dk() {
  dkdc "$@"
}

## Python
function ipython() {
  # python -c 'import IPython; IPython.terminal.ipapp.launch_new_instance()'
  uv run ipython || uvx ipython
}

function ipy() {
  # python -c 'import IPython; IPython.terminal.ipapp.launch_new_instance()'
  ipython
}

function eda() {
  python -c 'import IPython; IPython.terminal.ipapp.launch_new_instance()' -i eda.py
}

function di() {
  uv pip install --upgrade ipython ipykernel nbformat
}

function wp() {
  which python
}

function wp3() {
  which python3
}

function venv() {
  uv venv "$@"
}

function on() {
  . .venv/bin/activate
}

function off() {
  deactivate
}

function fmt() {
  ruff check --fix "$@"
  ruff check --select I --fix "$@"
  ruff format "$@"
}

function fmti() {
  ruff check --select I --fix "$@"
  ruff format "$@"
}

## Advanced Git
function gitfucked() {
    repo_name=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")
    if [ -z "$repo_name" ]; then
        echo "not in a git repository"
        return 1
    fi

    for i in {1..3}; do
        echo -n "are you sure you want to nuke the repo '$repo_name' at $(pwd)? [Y/N] "
        read response
        if [[ ! "$response" =~ ^[Y]$ ]]; then
            echo "operation cancelled"
            return 1
        fi
    done

    git update-ref -d HEAD && git add -A && git commit -m "initial commit" && git push --force
    echo "repository '$repo_name' has been reset"
}

## Drawing locally
function excalidraw() {
    (cd ~/code/excalidraw && yarn start)
}

function draw() {
  excalidraw
}

## Media utilities
function mp4() {
    local input_file="$1"
    local output_file="$2"
    
    # Check if input file is provided
    if [ -z "$input_file" ]; then
        echo "Error: Input file is required"
        echo "Usage: mp4 input_file [output_file]"
        return 1
    fi
    
    # If output file not provided, use input name with .mp4 extension
    if [ -z "$output_file" ]; then
        # Get base name of input file without extension
        local base_name="${input_file%.*}"
        output_file="${base_name}.mp4"
    fi
    
    echo "Converting $input_file to $output_file..."
    ffmpeg -i "$input_file" -c:v libsvtav1 -crf 30 -preset 8 -c:a aac -movflags +faststart "$output_file"
    
    # Check if conversion was successful
    if [ $? -eq 0 ]; then
        echo "Conversion completed successfully"
        return 0
    else
        echo "Conversion failed"
        return 1
    fi
}

function gif() {
    local input_file="$1"
    local output_file="$2"
    
    # Set up colors for interactive terminals
    if [ -t 1 ]; then
        yellow="\033[1;33m"
        red="\033[1;31m"
        cyan="\033[1;36m"
        reset="\033[0m"
    else
        yellow=""
        red=""
        cyan=""
        reset=""
    fi
    
    # Display help if no input file provided
    if [ -z "$input_file" ]; then
        echo -e "${yellow}Error: Input file is required${reset}" >&2
        echo -e "Easily convert a video to a gif using ffmpeg. This will optimize the color palette to" >&2
        echo -e "keep it looking good, and drop the framerate to 10fps to keep the file size down." >&2
        echo -e "${yellow}Usage: gif input_file [output_file]${reset}" >&2
        return 1
    fi
    
    # If output file not provided, use input name with .gif extension
    if [ -z "$output_file" ]; then
        # Get base name of input file without extension
        local base_name="${input_file%.*}"
        output_file="${base_name}.gif"
    fi
    
    # Ensure the input file exists
    if [ ! -f "$input_file" ]; then
        echo -e "${red}Error: Input file does not exist ${cyan}'$input_file'${reset}" >&2
        echo -e "${yellow}Usage: gif input_file [output_file]${reset}" >&2
        return 1
    fi
    
    echo "Converting $input_file to $output_file..."
    ffmpeg -i "$input_file" \
        -filter_complex "[0:v] fps=10,scale=640:-1:flags=lanczos,palettegen [p]; \
        [0:v] fps=10,scale=640:-1:flags=lanczos [x]; \
        [x][p] paletteuse" \
        "$output_file"
    
    # Check if conversion was successful
    if [ $? -eq 0 ]; then
        echo "Conversion completed successfully"
        return 0
    else
        echo "Conversion failed"
        return 1
    fi
}

