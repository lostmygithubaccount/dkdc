- go full monorepo:

we need to vendor in the functionality of `../files` and `../dotfiles`. for files:

- move `files` into here for real
- virtual files on top of our datalake, bootstrapped
- uilities for getting real files and stuff I guess
- but mostly just wrap, get strings, and pipe in/out of lake

for dotfiles:

- update .bash_aliases accordingly for stuff using the current files (same for dotfiles)
- vendor in the code into a `dotfiles/` directory
- update the install stuff and put it at the root
- add CLI commands like `sync` that are currently in bin
