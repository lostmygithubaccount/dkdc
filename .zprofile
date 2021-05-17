# export PATH
export PATH="~/miniconda3/bin:$PATH"
export PATH="/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin:$PATH"
#export PATH="/Applications/Visual Studio Code.app/Contents/Resources/app/bin:$PATH"
export PATH="/usr/local/opt/sqlite/bin:$PATH"

# time savers 
alias v='vi'
alias t='tree'
alias tt='tree -L 2'
alias ttt='tree -L 3'

# navigation
alias ..='cd ..'
alias ...='cd ../..'

# quick mafs 
alias ali='v ~/.zprofile'
alias update='source ~/.zprofile'

# make life easier 
alias du='du -h -d1 .'
alias yt='youtube-dl'
alias notes='vi ~/notes.md'
alias catnotes='cat ~/notes.md'
alias down="cd ~/Downloads"

# export Azure subscription id
export ID="6560575d-fa06-4e7d-95fb-f962e74efd7a"

# quick project access
alias azmlcli="cd ~/code/AzureMLCLI"
alias ex="cd ~/code/azureml-examples; conda activate dkdc"
alias docs="cd ~/code/azure-docs-pr/articles/machine-learning"
alias cheats="cd ~/code/azureml-cheatsheets"
alias mldiff="cd ~/code/mldiff; conda activate mldiff"
alias pl="cd ~/code/pl-learn; conda activate pl"
alias previews="cd ~/code/azureml-previews"

# i <3 msft
alias azcopy="~/azcopy/azcopy"
alias vsp="~/miniconda3/envs/dkdc/bin/python"

# python stuff
alias off="conda deactivate"
alias dkdc="conda activate dkdc"
#alias python="python3"
#alias pip="pip3"
