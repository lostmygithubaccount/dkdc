# dkdc

***don't know, don't care***.

> [!WARNING]
> ***Work in progress***.

## Setup

### Prerequisites

[Install uv](https://docs.astral.sh/uv/getting-started/installation):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

Install `dkdc`:

```bash
uv tool install dkdc
```

## Usage

Use `dkdc --help` for more information.

Enter a dev REPL connected to your datalake:

```bash
dkdc dev
```

Archive a directory to your datalake:

```bash
dkdc archive
```

Work in a virtual filesystem:

```bash
dkdc files
```

## Development

Clone the repository:

> [!WARNING]
> Install `gh`.

```bash
gh repo clone lostmygithubaccount/dkdc
cd dkdc
```

Set up the development environment:

```bash
./bin/setup.sh
```

Run code checks (lint & format):

```bash
./bin/check.sh
```

Run the development REPL:

```bash
uv run dkdc dev
```

## Organization

Code is organized:

- [`py/`](py): Python source code
- [`rs/`](rs): Rust source code
- [`go/`](go): Go source code
- [`bin/`](bin): Repository utilities
- [`tasks/`](tasks): Markdown tasks
- [`dotfiles/`](dotfiles): Dotfiles
- [`websites/`](websites): Static websites

## Rust CLIs

See [`dkdc-links`](rs/dkdc-links/README.md) for bookmarks in your terminal.
