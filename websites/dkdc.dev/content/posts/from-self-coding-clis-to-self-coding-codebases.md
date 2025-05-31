+++
title = "from self-coding CLIs to self-coding codebases"
date = "2025-04-28"
author = "Cody"
tags = ["ai"]
draft = true
+++

In ["modern agentic software engineering"](/posts/modern-agentic-software-engineering), I mentioned [I contributed to OpenAI's `codex`](https://github.com/openai/codex/pull/158). I don't have the exact prompt I used ([command history wasn't persisted until a little later](https://github.com/openai/codex/pull/152)), but it was trivial. I don't write JavaScript/TypeScript code, but I contributed with a self-coding CLI in a matter of minutes.

I had the idea for a self-coding CLI about 1.5 years ago:

{{< youtube bigVAU5d_6E >}}

It was pretty awful at this stage -- no automatic file writing (though it just added it!). [Aider was around (and head of its time)](https://github.com/Aider-AI/aider/tree/fcb209c5aa9b9c17d9aa7056b18c31309cb1ba3e) but I wouldn't hear about it until a few weeks ago; perhaps I should give it a more serious try (it looks slick, though I'm less-clear it can be as easily automated as `codex` or `claude`).

My latest attempt for [Ascend](https://ascend.io)'s hackday a few weeks ago, `OttoShell`, is decent and takes a novel approach of acting as a REPL with passthrough to your shell that passed into calls to the LLM via `? <prompt>`:

```bash
cody@dkdcascend ascend-io % os

 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░▌          ▐░▌
▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░▌
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌          ▐░▌
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌▐░░░░░░░░░░▌▐░░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░▌          ▐░▌
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░▌
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌          ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌
▐░█▄▄▄▄▄▄▄█░▌     ▐░▌          ▐░▌     ▐░█▄▄▄▄▄▄▄█░▌ ▄▄▄▄▄▄▄▄▄█▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄
▐░░░░░░░░░░░▌     ▐░▌          ▐░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀▀▀▀▀▀▀▀▀▀▀       ▀            ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀

(01001111 01110100 01110100 01101111 01010011 01101000 01100101 01101100 01101100)
~/code/ascend-io (os) > ai
╭──────────────────────────────────────────────────────────────╮
│ ● OpenAI Codex (research preview) v0.1.2504172351            │
╰──────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────╮
│ localhost session: 490c6deccda741c58c7680ac8cfdacef          │
│ ↳ workdir: ~/code/ascend-io                                  │
│ ↳ model: o4-mini                                             │
│ ↳ approval: full-auto                                        │
╰──────────────────────────────────────────────────────────────╯
user
who are you?

    codex
    I’m Codex, your AI-powered coding assistant running in this CLI environment. I can:

    • Interpret your prompts and navigate the codebase
    • Read, modify, and create files via shell commands
    • Run tests and linters to verify changes
    • Help debug, refactor, and document your code

    Let me know what you need help with next!
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ send a message                                                                                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
  send q or ctrl+c to exit | send "/clear" to reset | send "/help" for commands | press enter to send

~/code/ascend-io (os) > which ai
ai () {
        codex --full-auto "$@"
}
~/code/ascend-io (os) > ? who are you?
-----------------------------------------------------------------------------------------------------------------------------------------------
I am OttoShell, your terminal-based assistant developed by Ascend. I help you
with terminal tasks, especially around data engineering, DevOps, and software
development. How can I assist you today?
```

I used it to develop itself for several pieces (not the ASCII art!). It has prompt history, Vim keybindings, and more!

But `codex` (and `claude`, to a lesser extent in my opinion) is on another level. I'm excited about what I can accomplish between a terminal and a browser in 2025.

