+++
title = "OpenAI Codex CLI tips and tricks"
date = "2025-04-24"
author = "Cody"
tags = ["ai"]
draft = true
+++

I (and certainly others) realized the possibility of an agentic command line interface (CLI) -- the kind of tool that can code itself -- for a while now. [OpenAI's Codex CLI](https://github.com/openai/codex) is the first open source implementation of this idea ***that works extremely well***. I've been using `codex` extensively over the last week and wanted to share some tips and tricks that should generalize to any agentic CLI.

## mindset shift

[My readers are overwhelmingly experienced in AI](/source), so I'll avoid delving into details like what MCP is and assume you know how to use search engines and LLMs effectively for learning. It's important to take a step back and understand what makes agentic CLIs so unique:

- **Trivial parallelization**: if you can script it, you can parallelize it
- **Trivial automation**: if you can script it, you can automate it
- **Built-in best practices**: force developers to follow SWE best practices

**This take us up an abstraction level from GUI-based agentic software engineering**. That is, instead of encouraging a human developer to pair program with their IDE, we encourage human developers ***to automate their codebases with traditional [Unix-style](https://en.wikipedia.org/wiki/Unix_philosophy) tooling***.

## how `codex` works

```bash
gh repo clone openai/codex
cd codex
codex --full-auto "analyze the codebase and explain how codex does..."
```

## tips & tricks

### ***learn how it fucking works***

The height of intelligence is the ability to predict what happens next. If you're using AI agents without understanding on a mildly deep level how they work, you're doing it wrong. ***There is no magic and there are no shortcuts***.

The most important aspect of effective `codex` use is the ability to reliably solve real problems with it. This requires understanding what the tool will do when you use it and gain intuition for effective use.

### `git good`

You have to be good at `git` -- it's just a prerequisite. You need to actually learn the commands and how they work, not just rely on AI to do it for you. **But you should absolutely leverage AI to learn `git`, as it's exactly the type of thing it knows well.** ["Commits are snapshots, not diffs"](https://github.blog/open-source/git/commits-are-snapshots-not-diffs/) is a conceptual overview.

### in-repo, out-of-repo, and sub-directory context

### learn the iteration process

### using different modes in `codex`

By default, I call `codex` as `codex --full-auto` (I have a ~~bash~~ zsh ~~alias~~ function for this as `ai`). In niche scenarios, I call `codex` as-is and have it ask me before doing things. I use `codex --quite --full-auto` in 

- `codex`: the default mode, where it asks for confirmation before doing anything
- `codex --full-auto`: automatically edit files & run commands (this should be your default for interactive use)
- `codex --full-auto --quiet`: don't return a REPL at the end (this is for full automation)

You should start with the default mode and see how it works, but should quickly switch to `--full-auto` for interactive use. Once you iterate interactively and have your `task.md` file working reliably, try it with `--full-auto --quiet` and fully automate the task in your codebase!

### give `codex` tools as CLIs

`codex` works with MCP, but you almost certainly shouldn't use it.

### use `ai.md`* files effectively

*`ai.md` isn't a real standard...yet...

### use a `task.md` file

### extend to a `ai/tasks/` directory

### automate your codebase

The general workflow is:

- (**don’t skip**) have a well-structured, well-documented code repository
- (**don’t skip**) have a code repository with good, fast linting and tests
- iterate with `task.md` files with all relevant out-of-repo context
- automate with `ai/tasks/<task-name>.md` files, scripts, and CI/CD

It's going to be difficult to automate your codebase until you have a codebase junior developers and agentic software engineering tools can effectively operate in. You can use `codex` to help get there, but don't rely on LLMs to architect your codebases (do use them for ideas or to learn about tools that may help, and to do the actual coding as useful).

### use non-deterministic tools wisely

Everything that can be coded determinstically should be. Introducing `codex` or any agentic tool into your processes introduces risk.

### flip the script

## a crazy idea (prediction)

I don't want to give too much away, but as a quick thought experiment imagine you're building a new project from the ground up. You're personally proficient in Python and Go, and somewhat know Rust.

***This is dramatically more possible today than it was a week ago.***
