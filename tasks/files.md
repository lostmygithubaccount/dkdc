I use a `files/` repo. In the spirit of moving everything into this monorepo, I want to replace this using the data lake we have here. Files should never directly be placed on disk because through the datalake they are always encrypted.

These files are special too -- right now we only have:

- `life.md`: TODO list for life
- `work.md`: TODO list for work
- `pri.md`: priority reminders
- `notes.md`: scratch notes

Evaluate my `dotfiles/.bash_aliases` and note how I'm using these files.

What I suspect we'll want is `dkdc files <filename>` that opens the given filename in a "virtual filesystem" of sorts. I.e. if the file doesn't exist, we create it with those contents.

I'm not sure how this can work with neovim. When I call `dkdc files todo`, I want it to open the corresponding todo files. The path should probably be `./files/work.md` or similar, BUT NOT ACTUALLY BE CREATED HERE RIGHT.

Confirm this makes sense, analyze the codebase, and propose a simple implementation of this new feature.
