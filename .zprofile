# time savers 
alias v='vi'

# navigation
alias ..='cd ..'
alias ...='cd ../..'

# quick mafs 
alias ali='v ~/.zprofile'
alias update='source ~/.zprofile'

# conda envs 
alias dkdc='conda activate dkdc'

# make life easier 
alias du='du -h -d1 .'

# make python great again 
alias pip='noglob pip'
alias python='~/opt/miniconda3/envs/dkdc/bin/python'
alias nbclear='jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace'

# export PATH
export PATH="~/opt/miniconda3/bin:$PATH"
#export PATH="/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin:$PATH"
export PATH="/Applications/Visual Studio Code.app/Contents/Resources/app/bin:$PATH"
export PATH="/usr/local/opt/sqlite/bin:$PATH"
