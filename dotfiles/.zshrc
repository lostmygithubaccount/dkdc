# Standard stuff
if [ -f "$HOME/.env" ]; then
    source "$HOME/.env"
fi

if [ -f $HOME/.bash_aliases ]; then
    . $HOME/.bash_aliases
fi

# Docker (move this?)
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# Ascend-specific stuff
## Path
export PATH="$HOME/google-cloud-sdk/bin:$PATH" # ugh
export PATH="/opt/homebrew/opt/mysql@8.4/bin:$PATH"

## Miscellaneous
ulimit -n 2560 # some bizarre issue
eval "$(fnm env --use-on-cd --shell zsh)" # Node nonsense

## Environment variables
export VPS_IP="178.128.12.54"

export ASCEND_INFRA="$HOME/code/ascend-io/infra" # Infra repo location
# export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
# export PYENV_ROOT="$HOME/.pyenv"
# [[ -d $PYENV_ROOT/shims ]] && export PATH="$PYENV_ROOT/shims:$PATH"
#export PATH="$HOME/code/ascend-io/source/bin:$PATH"
### Repos
export PRODUCT="ascend-io/product"
export CORE="ascend-io/ascend-core"
export BACKEND="ascend-io/ascend-backend"
export FRONTEND="ascend-io/ascend-ui"
export INFRA="ascend-io/ascend-infra"
export DOCS="ascend-io/ascend-docs"
export COMMUNITY="ascend-io/ascend-community-internal"
export BASECAMP="ascend-io/basecamp"

# Zsh autocomplete
autoload -Uz compinit
compinit

# Enable version control info (fast mode - with change indicators)
autoload -Uz vcs_info
zstyle ':vcs_info:git:*' formats '%b%c%u'
zstyle ':vcs_info:*' check-for-changes true
zstyle ':vcs_info:*' unstagedstr '%F{160}*%f'  # Darker red for better contrast on pink
zstyle ':vcs_info:*' stagedstr '%F{30}+%f'     # Darker cyan for better contrast

# Prompt configuration
setopt PROMPT_SUBST

# Modern gradient powerline colors  
local bg_time='%K{236}'       # Darker grey background for timestamp
local fg_time='%F{255}'       # White text
local bg_elapsed='%K{240}'    # Grey background for elapsed time
local fg_elapsed='%F{255}'    # White text
local bg_user='%K{99}'        # Purple background
local fg_user='%F{255}'       # White text
local bg_path='%K{135}'       # Bright magenta background  
local fg_path='%F{255}'       # White text
local bg_git_clean='%K{87}'   # Cyan background for clean
local fg_git_clean='%F{0}'    # Black text
local bg_git_dirty='%K{213}'  # Subtle pink background for dirty  
local fg_git_dirty='%F{0}'    # Black text
local reset='%k%f'            # Reset all colors

# Powerline separators
local sep_right=''           # Right-pointing triangle
local sep_left=''            # Left-pointing triangle

# Container detection
container_indicator() {
    if [[ -n "$CONTAINER_ID" || -n "$HOSTNAME" && "$HOSTNAME" =~ ^[a-f0-9]{12}$ || -f /.dockerenv || -n "$CODESPACES" ]]; then
        echo "🤖 "
    fi
}

# Fish-style directory collapsing
fish_style_pwd() {
    local pwd_path="$PWD"
    local home_path="$HOME"
    
    # Replace home with ~
    if [[ "$pwd_path" == "$home_path"* ]]; then
        pwd_path="~${pwd_path#$home_path}"
    fi
    
    # If path is short enough, return as-is
    if [[ ${#pwd_path} -le 32 ]]; then
        echo "$pwd_path"
        return
    fi
    
    # Split path and collapse middle directories
    local parts=(${(s:/:)pwd_path})
    local result=""
    local parts_count=${#parts}
    
    if [[ $parts_count -le 4 ]]; then
        echo "$pwd_path"
        return
    fi
    
    # Always show first part (~ or /)
    result="${parts[1]}"
    
    # Always show second part in full if it exists
    if [[ -n "${parts[2]}" ]]; then
        result="$result/${parts[2]}"
    fi
    
    # Collapse middle parts to first character (skip first, second, and last two)
    for ((i=3; i<parts_count-1; i++)); do
        if [[ -n "${parts[i]}" ]]; then
            result="$result/${parts[i]:0:1}"
        fi
    done
    
    # Always show last two parts in full
    if [[ parts_count -ge 2 && -n "${parts[parts_count-1]}" ]]; then
        result="$result/${parts[parts_count-1]}"
    fi
    if [[ -n "${parts[parts_count]}" ]]; then
        result="$result/${parts[parts_count]}"
    fi
    
    echo "$result"
}

# Git status helper (fast mode - no network operations)
git_prompt_info() {
    if [[ -n "${vcs_info_msg_0_}" ]]; then
        local git_info="${vcs_info_msg_0_}"
        
        # Check if repo has any changes (staged or unstaged) - but skip network operations
        if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
            echo "${bg_git_dirty}${fg_git_dirty} ${git_info} ${reset}%F{213}${sep_right}${reset}"
        else
            echo "${bg_git_clean}${fg_git_clean} ${git_info} ${reset}%F{87}${sep_right}${reset}"
        fi
    else
        echo "%F{135}${sep_right}${reset}"
    fi
}

# Timestamp helper
get_timestamp() {
    TZ=UTC date '+%Y/%m/%d %H:%M:%S'
}

# Command timing
typeset -g _command_start_time
typeset -g _last_command_duration

# Hook to record command start time
preexec() {
    _command_start_time=$SECONDS
    _last_command_duration=""  # Clear previous duration when new command starts
}

# Hook to calculate elapsed time after command completes
precmd() {
    vcs_info  # Keep existing vcs_info functionality
    
    if [[ -n $_command_start_time ]]; then
        local elapsed=$(( SECONDS - _command_start_time ))
        _last_command_duration=$(printf "%d" $elapsed)
        unset _command_start_time
    fi
}

# Get the stored elapsed time
get_elapsed_time() {
    if [[ -n $_last_command_duration ]]; then
        echo "$_last_command_duration"
    fi
}

# Build the modern gradient powerline prompt (single line + newline prompt)
PROMPT='$(container_indicator)'                                                          # Container indicator
PROMPT+="${bg_user}${fg_user} %n@%m ${reset}%F{99}${sep_right}${reset}"               # Purple user@hostname segment  
PROMPT+="${bg_path}${fg_path} \$(fish_style_pwd) ${reset}%F{135}${sep_right}${reset}" # Magenta path segment
PROMPT+="\$(git_prompt_info)"                                                          # Cyan/pink git segment
PROMPT+="${bg_time}${fg_time} \$(get_timestamp) ${reset}%F{236}${sep_right}${reset}"  # Darker grey timestamp segment
PROMPT+="\$([ -n \"\$(get_elapsed_time)\" ] && echo \"${bg_elapsed}${fg_elapsed} \$(get_elapsed_time) ${reset}%F{240}${sep_right}${reset}\")"  # Grey elapsed time segment
PROMPT+=$'\n'                                                                          # Newline
PROMPT+="%F{99}❯%f "                                                                   # Violet prompt character

