# dkdc

***Don't know, don't care***.

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

Backup a directory to your datalake:

```bash
dkdc backup
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

Run code checks:

```bash
./bin/check.py
```

Run the development REPL:

```bash
uv run dkdc dev
```
