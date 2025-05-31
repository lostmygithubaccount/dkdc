+++
title = "modern agentic software engineering"
date = "2025-04-21"
author = "Cody"
tags = ["ai"]
draft = false
+++

OpenAI's [`codex`](https://github.com/openai/codex) has demonstrated something I've struggled to for a while: we've been doing AI software engineering wrong. Or at least, there's a better way with CLIs and files as the interface. What's [old](https://en.wikipedia.org/wiki/Unix_philosophy) is new again.

<!-- more -->

In this post, I demonstrate the core workflow for modern agentic software engineering that can be applied to pair-programming or automation via CI/CD:

- (**don't skip**) have a well-structured, well-documented code repository
- (**don't skip**) have a code repository with good, fast linting and tests
- generate a `task.md` file with all relevant out-of-repo context
- `ai "open the task.md and work on it"`
- further wrap this workflow with scripts for automation when appropriate

{% details(summary="Click for some pro tips") %}

- `gh issue view NUMBER > task.md` and such...
- if working interactively, supervise and iterate
- if working in CI/CD, make a PR and review (noting you can loop agentic reviews in here...)
- consolidate commands for linting and testing in a `Makefile` or similar (I like `justfile`) and instructions your `ai` on using them
- ideate, learn, do, iterate, automate

{% end %}

You can then leverage standard [software development lifecycle (SDLC)](https://en.wikipedia.org/wiki/Software_development_process) best practices and GitOps for modern agentic software engineering.

## a toy example

In writing this post I wanted to preview this website locally. It wasn't working for only this post and I was very confused (I just re-wrote this website into a new framework today, or rather yesterday...). In my terminal, side-by-side with this post open in my editor, I typed `ai "for some reason modern-agentic-software-engineering.md in posts/ isn't showing up in my build, any ideas?"` and got:

{% details(summary="Click to expand `codex` session") %}

```bash
╭──────────────────────────────────────────────────────────────╮
│ ● OpenAI Codex (research preview) v0.1.2504172351            │
╰──────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────╮
│ localhost session: 55768aecf37642c2b407726b45aab06f          │
│ ↳ workdir: ~/code/dkdc-io/dkdc.dev/website                   │
│ ↳ model: o4-mini                                             │
│ ↳ approval: full-auto                                        │
╰─────────────────────────────────────────────────────────────╯
user for some reason modern-agentic-software-engineering.md in posts/ isn't showing
up in my build, any ideas?

    Inspecting Hugo structure

    The user is working with a Hugo-based personal website, and the file
    modern-agentic-software-engineering.md in posts/ isn’t showing up in the build.
    I need to figure out Hugo's content directory structure. While the standard
    content directory is typically content/, it's unclear if posts/ is under
    content/posts or at the root. I should examine the repository structure.
    I'll look into the directories by running a command to list the structure
    so we can get clarity.

    command

    $ ls -R .

    command.stdout (code: 0, duration: 0s)

    archetypes codex.md content data ... (381 more lines)

    Inspecting markdown file

    I see that the markdown file is located in the content/posts directory,
    specifically at content/posts/modern-agentic-software-engineering.md. The user
    mentioned it isn't showing up in the build. This suggests I should inspect
    the markdown file for potential issues, like front matter problems. I'll go
    ahead and check the file's content to identify any errors that might be
    preventing it from being included in the build process. Let's see what's
    going on!

    command

    $ sed -n '1,200p' content/posts/modern-agentic-software-engineering.md

    command.stdout (code: 0, duration: 0s)

    +++ title = "modern agentic pair programming" date = "2025-04-21" author =
    "Cody" ... (15 more lines)

    Investigating Hugo site issues

    I see that the content has proper front matter, and while there's no
    index.md file, that's okay since Hugo should handle .md files within posts.
    I'm wondering if taxonomy settings in hugo.toml are misconfigured or if the
    section name is incorrect. The posts should be listed under public/posts,
    but I can't find modern-agentic-software-engineering there. I'll need to check
    the file's presence and ensure everything is set correctly for proper
    display.

    Analyzing Hugo's posting issue

    It looks like Hugo skipped generating a folder for the post. I'm wondering
    if it’s due to the file naming or perhaps the post being future dated. The
    file is located at content/posts/modern-agentic-software-engineering.md, which
    should create an index.html in public/posts, but it doesn't. Since the date
    is set to 2025-04-21 and today is 2025-04-20, Hugo defaults to not
    publishing future content. I need to check the date settings for other
    posts to confirm this.

    command

    $ grep -R "date =" -n content/posts/context-length-pain.md

    command.stdout (code: 0, duration: 0s)

    content/posts/context-length-pain.md:3:date = "2023-08-13"


    command

    $ sed -n '1,200p' justfile

    command.stdout (code: 0, duration: 0s)

    # Justfile

    # load environment variables set dotenv-load ... (40 more lines)

    command

    $ sed -n '1,200p' hugo.toml

    command.stdout (code: 0, duration: 0s)

    baseURL = 'https://dkdc.dev' languageCode = 'en-us' title = 'dkdc.dev'
    theme = ["terminal"] ... (22 more lines)

    command

    $ sed -n '200,400p' hugo.toml

    command.stdout (code: 0, duration: 0s)


    Explaining build settings

    I see the user is having an issue with their Hugo site where a post isn't
    showing up. By default, Hugo doesn't build future-dated posts since
    buildFuture is set to false. If the user wants to include future posts,
    they need to change buildFuture to true in the config or adjust the post
    date to today or earlier. Since there's no extra context, I’ll suggest they
    check their post date or run the command to allow future posts.

    Fixing Hugo future posts

    It seems the issue is that Hugo is skipping future-dated content. To fix
    this, the user can either change the post date to today or run the command
    hugo server -D -F to include drafts and future posts. They mentioned that
    the file date is set to "2025-04-21", but the system date is "2025-04-20".
    I’ll suggest checking the front matter date and confirm its accuracy.
    Additionally, the user could set buildFuture = true in the config if they
    want future posts included. I'll verify the correct configuration.

    codex It turned out nothing was wrong with Hugo or your file‑layout – Hugo
    simply skipped it because its date is “in the future.” Your front‑matter
    says:

      date = "2025‑04‑21"

    but today (per your build) is 2025‑04‑20, so by default Hugo won’t render
    it until that date arrives.

    You have a couple of easy options:

    • Lower the date to today (or earlier), e.g. date = "2025‑04‑20"

    • When you preview, tell Hugo to include future posts: just preview -D -F
    (that’s hugo server -D -F under the hood)

    • For a one‑off production build that includes future posts: hugo
    --buildFuture --minify

    If you’d rather always build future content you can also add the CLI flag
    to your build recipe or wrap it into your hugo.toml, but most folks simply
    update the date when they’re ready to publish.
```

{% end %}

Summarizing:

- I was writing the post on April 20, 2025
- The post was dated April 21, 2025
- Hugo by default doesn't include posts in the future in its preview or build

Instead of going down some rabbit hole on some ad-riddled website, I just "asked" my terminal around where the problematic file was. You may have noticed before reading any files it noted:

```txt
Inspecting Hugo structure

The user is working with a Hugo-based personal website...
```

Where did this information come from? And what makes this pattern so powerful?

## a couple of 3 things

There are 3 things that are revolutionary here for agentic software engineering:

1. Dynamic in-repo context
1. Using CLIs directly
1. Files (strings) as the interface

### dynamic in-repo context

`codex` (uniquely as of release?) works off `codex.md` files **per-directory**. You can also set global instructions in `$HOME/.codex/instructions.md` by default (use `codex --config/-c` to quickly open global instructions in `$EDITOR`). This means as your agent navigates down the file tree you give it access to, it's dynamically loading relevant context per-directory. This solves a lot of issues with supplying relevant context to agents that is a lot more natural than alternatives.

You can structure repos and directories like:

```
./
├── repoA/
│   ├── subdirA/
│   │   └── codex.md
│   ├── subdirB/
│   │   └── codex.md
│   └── codex.md
├── repoB/
│   └── codex.md
└── repoC/
    └── codex.md
```

This explains how `codex` knew details about my website's codebase earlier, and has directory-specific context for other repositories I work in. Your `task.md` just needs any context that doesn't already exist in the filetree.

### using CLI commands directly

SQL is one of the most popular "programming languages" in the world, despite software engineers not thinking of it as such often. Why? Largely because it's declarative and reads like English. `SELECT * FROM people WHERE age > 21` kinda makes sense even if you don't code. It's easy to learn and (relatively) limited in scope while allowing users to accomplish a lot.

Similarly, `gh pr list` is a CLI command that probably just makes sense (assuming you know what `gh` and `pr` are, to be fair). And if they don't, just `ai "explain <whatever>"`! `codex` uses CLI tools directly, allowing you to use the same tools and automate repeated actions for human or agentic use. To demonstrate, early `codex` didn't use a special tool to read a file, just `sed` like:

```bash
$ sed -n '1,200p' content/posts/modern-agentic-software-engineering.md
```

or `grep` to search files:

```bash
$ grep -R "date =" -n content/posts/context-length-pain.md
```
The broader point here is **LLMs are trained on human text and work best like humans interacting with text**. Working via CLIs (which also solve a lot of client/server interaction problems) is a natural fit. And CLIs have good built-in documentation (for humans or agents) via `--help/-h` flags. It's easy to use the exact same tools your agent uses and ***write any deterministic workflows into reusable scripts*** that humans, agents, or CI/CD can run again and again.

### files (strings) as the interface

Working with LLMs is easiest when you think of them as autoregressive text processors. This explains a lot of their behavior: why they struggle to generate ASCII art, why they can't reliably do math, etc. If this doesn't make sense, you should learn more about neural networks and modern LLMs until it does.

Once you do, you understand the text (string) data that goes into the LLM is essentially all that matters: text in, text out. Getting that input text data fast and efficiently is critical to modern agentic software engineering. The [Unix philosophy](https://en.wikipedia.org/wiki/Unix_philosophy) largely solves this and many more problems with effective use.

I'm standardizing on a `task.md` convention for loading all relevant context before my `ai` call (`ai "open the task.md and work on it"`).

## how I use `git`, `gh`, `nvim`, `tmux`, and `codex`

I have a love/hate relationship with typing. I use a lot of ~~bash~~ zsh ~~aliases~~ functions like:

```bash
function ai() {
  codex --full-auto "$@"
}

function v() {
  nvim "$@"
}

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

function taskit() {
    echo "# PR description" > task.md
    gh pr view >> task.md
    echo "# PR comments" >> task.md
    gh pr view -c >> task.md
    echo "# PR diff" >> task.md
    gh pr diff >> task.md
    echo "# PR review comments" >> task.md
    ghprc >> task.md
}
```

(as an exercise for the reader, without copy/pasting from your browser, pipe the code above for `ghprc` into `codex` to explain it)

I like to think of this as a form of **automation**. If I can automatically build a `task.md` quickly, I can `ai "open the task.md and work on it"` for **any task**. It's just about quickly building up the `task.md` that will accomplish what I want.

Git is critical for managing strings in the filesystem. Vim keybindings make editing `task.md` files to feed into `codex` fast. Tmux allows me to have my editor and `ai` open side-by-side, and open new windows as needed for more sessions in parallel. And the GitHub CLI + my bash functions help pull information from software engineers I work with into the `task.md` file. If your GitHub issues are well-written, there's no reason `gh issue view NUMBER | codex --full-auto` shouldn't be your first attempt at solving a problem. Though until you and your team adopt this new paradigm, you might want to start with `gh issue view NUMBER >> task.md` and edit manually. Do what works!

## BUT WHAT ABOUT

But what about [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)?? They even released first! And actually, there's [Aider](https://aider.chat)! And that's already open source, and they've been doign it forever!1!!

Yes. But `claude` isn't open source (and thus doesn't have a `--config/-c` flag added by me, making it inferior) and `aider` is...just not quite the same level of agentic in my admittedly inexperienced opinion. OpenAI's `codex` is the first where the workflow has clicked for me, though I've been using `claude` more side-by-side and it's also fine. I'm more concerned with the workflow than the provider/specific tool.

Claude Code, as of this post, does not support `CLAUDE.md` files in subdirectories that are used in the same way `codex.md` files are (as far as I can tell from usage and their documentation). I'm less-sure, but believe loading context into Aider is a more manual process as well. These tools will converge on doing whatever works best, and I suspect both will soon do this as `codex` does.

Oh and what about RAG! Using `grep`? So limiting! Vector search!!!

This last one might be a fair point -- and my counterpoint is if semantic vector search is so useful on its own, it should be its own CLI tool alongside `grep` for filesystem search. Why limit it to just agents? Modern agentic pair programming implies using the best tool for humans and agents alike, which tend to be open source standards and CLIs following the [Unix philosophy](https://en.wikipedia.org/wiki/Unix_philosophy).

## results

But where are the results!?!?!? In this post, I've only answered one (somewhat) simple question with `codex`.

While I can't share the code, in the past 2 weeks using agentic software engineering (`claude`, VSCode Copilot agent mode, `codex`) I've made **eight meaningful contributions to our frontend codebase** that, as a product manager and JavaScript hater, I would never have made otherwise -- my prior contributions were all updating strings in a `en-US.json` file. There's still reason to be skeptical but the evidence is mounting and the usefulness is getting easier to scale. I've also redone my personal website, refactored stuff into Go and Rust, and more with agentic assistance. Learning things yourself is important (and critical for effective use of agents), but the results are here now.

## predictions

I predict:

1. We standardize on `README`/`README.md`/`readme.md`/etc. instead of LLM-specific filenames for dynamic context across tooling. Why should the instructions for humans versus agents differ anyway? It should be assumed everyone working in the codebase read the `README` (crazy stuff).
2. Specialized domain-specific wrappers around standard software engineering agents emerge. Organizations and teams developer their own business logic as usual around these.
3. More people will realize the power of terminal-driven, file-driven agentic pair programming.
4. More people will realize the power of the above for agentic CI/CD.
5. Automation, automation, automation...

