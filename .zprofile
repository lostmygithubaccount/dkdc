# export PATH
export PATH="~/miniconda3/bin:$PATH"
export PATH="/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin:$PATH"
#export PATH="/Applications/Visual Studio Code.app/Contents/Resources/app/bin:$PATH"
export PATH="/usr/local/opt/sqlite/bin:$PATH"

# time savers 
alias v='vi'
alias t='tree'
alias l='less'
alias tt='tree -L 2'
alias ttt='tree -L 3'
alias ls='ls -1pG'

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
alias ex="cd ~/code/azureml-examples"
alias pp="cd ~/code/azureml-previews"
alias docs="cd ~/code/azure-docs-pr/articles/machine-learning"
alias cheats="cd ~/code/azureml-cheatsheets"
alias mldiff="cd ~/code/mldiff"
alias pl="cd ~/code/pl-learn"
alias previews="cd ~/code/azureml-previews"
alias sdk2="cd ~/code/sdk-cli-v2"
alias rest2="cd ~/code/vienna"

# i <3 msft
alias azcopy="~/azcopy/azcopy"
alias vsp="~/miniconda3/envs/dkdc/bin/python"

# python stuff
alias off="conda deactivate"
alias dkdc="conda activate dkdc"
alias python="python3"
alias pip="pip3"

# docker stuff
alias dit="docker run -it --rm"
alias dvit="dit -v /var/run/docker.sock:/var/run/docker.sock -v /Users/cody/.gitconfig:/users/cody/.gitconfig -v /Users/cody/.ssh:/users/cody/.ssh -v /Users/cody/.config:/users/cody/.config -v /Users/cody/.azure:/users/cody/.azure -v /Users/cody/code:/users/cody/code -v /Users/cody/.vscode:/users/cody/.vscode -v /Users/cody/.vscode-insiders:/users/cody/.vscode-insiders"
alias dvitp="dvit -p 8787:8787"
alias dev="dvitp --name dev lostmydockeraccount/main"
