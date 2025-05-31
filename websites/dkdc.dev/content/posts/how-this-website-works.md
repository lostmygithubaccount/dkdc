+++
title = "how this website works"
date = "2025-04-23"
author = "Cody"
tags = ["self"]
draft = true
+++

## publishing (releasing)

My release command is:

```bash
gsutil -m rsync -d -r public/ gs://dkdc.dev
```

That is, `rsync` a local directory to cloud object storage. Pretty nice.

## the `justfile`

I use [`just`](https://github.com/casey/just) (similar to [`task`](https://github.com/go-task/task) or `make`) to manage repo-specific commands. 

{% details(summary="dkdc.dev's `justfile`") %}

```makefile
# aliases
alias publish:=release

# list justfile recipes
default:
    just --list

# preview
preview *args:
    hugo server -OF {{ args }}

# preview with drafts
previewd:
    just preview -D

# build
build:
    hugo --buildFuture --minify

# release
release: build
    gsutil -m rsync -d -r public/ gs://dkdc.dev
    
# uncache
uncache:
    gcloud compute url-maps invalidate-cdn-cache dkdc-dev-lb --path "/*" --project dkdcwebsite --async

# config
config:
    $EDITOR hugo.toml

# clean
clean:
    rm -rf public
```

{% end %}

Due to the `release: build` in my `justfile`, running `just release` builds my website then syncs the local build directory (`public/`) to a Google Cloud Storage (GCS) bucket. That bucket is publicly viewable and serves the content of my website. You can now view the website at https://storage.googleapis.com/dkdc.dev/index.html. But you're (probably) on https://dkdc.dev...

## generating the `public/` directory

I use:

```bash
hugo --buildFuture --minify
```

(the `--buildFuture` to build posts dated in the future per [`ai`](/posts/modern-agentic-software-engineering#a-toy-example))

## how long does this take to setup?

I **strongly recommend** you take the time to understand how everything works at each step. If you already do, setting this up (assuming you already have a Google Cloud account) could speedrun this in a few minutes.

The more important point is the **why** behind hosting a static website like this.

## why?

1. **Simplicity**: the best UX
1. **Minimal lock-in**: I can easily switch to another web host
1. **Minimum viable process**: encourage writing by avoiding complexity

