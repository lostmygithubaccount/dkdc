# Base image
# TODO: if not using a Microsoft base image causes issues, switch to it and install uv via https://docs.astral.sh/uv/guides/integration/docker/#installing-uv (also check if there is slim version)
# FROM mcr.microsoft.com/devcontainers/base:debian
FROM ghcr.io/astral-sh/uv:debian-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    fuse \
    sudo \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create dev user with sudo privileges
RUN groupadd -g 1000 dev && \
    useradd -m -s /bin/zsh -u 1000 -g 1000 -G sudo dev && \
    echo 'dev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R dev:dev /home/dev

# Install development tools
RUN apt-get update && apt-get install -y \
    tree \
    ripgrep \
    btop \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Install latest Neovim from pre-built tarball
RUN curl -L https://github.com/neovim/neovim/releases/download/v0.10.2/nvim-linux64.tar.gz | tar -xz -C /opt && \
    ln -sf /opt/nvim-linux64/bin/nvim /usr/local/bin/nvim && \
    ln -sf /usr/local/bin/nvim /usr/local/bin/vim && \
    ln -sf /usr/local/bin/nvim /usr/local/bin/vi

# Install fnm (Fast Node Manager)
RUN curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir /usr/local/bin

# Switch to dev user for remaining setup
USER dev
WORKDIR /home/dev

# Set up fnm environment
ENV FNM_DIR="/home/dev/.fnm"
ENV PATH="/usr/local/bin:$PATH"

# Install Node.js versions for dev user
RUN /bin/bash -c 'eval "$(/usr/local/bin/fnm env --shell bash)" && \
    fnm install 20 && \
    fnm install 22 && \
    fnm default 22'

# Set up shell integration for fnm (bash and zsh) for dev user
RUN echo 'eval "$(/usr/local/bin/fnm env --shell bash)"' >> /home/dev/.bashrc && \
    echo 'eval "$(/usr/local/bin/fnm env --shell zsh)"' >> /home/dev/.zshrc

# Install Claude Code and OpenAI Codex CLI tools for dev user
RUN /bin/bash -c 'eval "$(/usr/local/bin/fnm env --shell bash)" && \
    npm install -g @anthropic-ai/claude-code@latest && \
    npm install -g @openai/codex@latest'

# Apply surgical patch to fix Claude Code ANTHROPIC_API_KEY bug (line 1965)
# This removes the &&!1 pattern that prevents environment variables from working
RUN /bin/bash -c 'eval "$(/usr/local/bin/fnm env --shell bash)" && \
    CLAUDE_CLI_PATH=$(which claude) && \
    if [ -f "$CLAUDE_CLI_PATH" ]; then \
        echo "Patching Claude Code at: $CLAUDE_CLI_PATH" && \
        sed -i "s/&&!1//g" "$CLAUDE_CLI_PATH" && \
        if grep -q "process\.env\.ANTHROPIC_API_KEY.*OyA" "$CLAUDE_CLI_PATH" && ! grep -q "&&!1" "$CLAUDE_CLI_PATH"; then \
            echo "✓ Claude Code ANTHROPIC_API_KEY patch applied successfully"; \
        else \
            echo "✗ Claude Code patch verification failed" && exit 1; \
        fi; \
    else \
        echo "✗ Claude CLI not found for patching" && exit 1; \
    fi'

# Python environment - install with cache mount for dev user
RUN --mount=type=cache,target=/home/dev/.cache/uv,uid=1000,gid=1000 \
    uv python install 3.13 \
    && uv python install 3.12 \
    && uv python install 3.11 \
    && uv python pin --global 3.13

# Python development tools - install with cache mount for dev user
RUN --mount=type=cache,target=/home/dev/.cache/uv,uid=1000,gid=1000 \
    uv tool install ruff \
    && uv tool install pytest \
    && uv tool install ranger-fm \
    && uv tool install pre-commit \
    && uv tool install ipython

# Prevent future Python downloads and make tools available
ENV UV_PYTHON_DOWNLOADS=never

# Create a workspace directory and set proper ownership
RUN sudo mkdir -p /workspace && sudo chown dev:dev /workspace
WORKDIR /workspace

# Set the default shell
SHELL ["/bin/zsh", "-c"]

# Set the default command to run when the container starts
CMD ["/bin/zsh"]
