# dkdc-links

***Bookmarks in your terminal.***

## Setup

### Prerequisites

[Install Rust and Cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html):

```bash
curl https://sh.rustup.rs -sSf | sh
```

### Installation

Install [`dkdc-links`](https://crates.io/crates/dkdc-links):

```bash
cargo install dkdc-links
```

> [!TIP]
> Consider aliasing `dkdc-links` to `links` or similar.

## Usage

To view aliases and links:

```bash
dkdc-links
```

To open aliases and links:

```bash
dkdc-links alias1 link1
```

To edit aliases and links:

> [!TIP]
> Configure `$EDITOR` to use your preferred text editor.

```bash
dkdc-links --config
```

Use `dkdc-links --help` for more information.
