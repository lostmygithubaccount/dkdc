# Base image
FROM ghcr.io/astral-sh/uv:debian-slim

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    jq \
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
    tree \
    tmux \
    ripgrep \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Create dev user with sudo privileges
RUN groupadd -g 1000 dev && \
    useradd -m -s /bin/zsh -u 1000 -g 1000 -G sudo dev && \
    echo 'dev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install fnm (Fast Node Manager)
RUN curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir /usr/local/bin

# Install Zola (static site generator)
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then ZOLA_ARCH="x86_64-unknown-linux-gnu"; \
    elif [ "$ARCH" = "arm64" ]; then ZOLA_ARCH="aarch64-unknown-linux-gnu"; \
    else echo "Unsupported architecture: $ARCH" && exit 1; fi && \
    wget https://github.com/getzola/zola/releases/download/v0.20.0/zola-v0.20.0-${ZOLA_ARCH}.tar.gz && \
    tar xzf zola-v0.20.0-${ZOLA_ARCH}.tar.gz && \
    mv zola /usr/local/bin/zola && \
    chmod +x /usr/local/bin/zola && \
    rm zola-v0.20.0-${ZOLA_ARCH}.tar.gz

# Create app directory
WORKDIR /app

# Copy only dependency files first (for better caching)
COPY pyproject.toml uv.lock* /app/
COPY package*.json /app/

# Copy the rest of the project files
COPY . /app

# Switch to dev user for remaining setup
USER dev
WORKDIR /home/dev

# Set up fnm environment
ENV FNM_DIR="/home/dev/.fnm"
ENV PATH="/home/dev/.local/bin:/home/dev/.fnm/aliases/default/bin:/usr/local/bin:$PATH"

# Set cache directories for better volume mounting
ENV UV_CACHE_DIR="/home/dev/.cache/uv"
ENV npm_config_cache="/home/dev/.cache/npm"

# Install Node.js 22 and set as default
RUN /bin/bash -c 'eval "$(/usr/local/bin/fnm env --shell bash)" && \
    fnm install 22 && \
    fnm default 22'

# Set up shell integration for fnm (bash and zsh)
RUN echo 'eval "$(/usr/local/bin/fnm env --shell bash)"' >> /home/dev/.bashrc && \
    echo 'eval "$(/usr/local/bin/fnm env --shell zsh)"' >> /home/dev/.zshrc

# Install Node.js tools
RUN /bin/bash -c 'eval "$(/usr/local/bin/fnm env --shell bash)" && \
    npm install -g @anthropic-ai/claude-code@latest && \
    npm install -g pyright && \
    npm install -g sql-language-server'

# Python environment - install with cache mount for dev user
RUN uv python install 3.13 \
    && uv python install 3.12 \
    && uv python install 3.11 \
    && uv python pin --global 3.13

# Install Python development tools
RUN uv tool install ruff && \
    uv tool install pytest && \
    uv tool install ranger-fm && \
    uv tool install pre-commit && \
    uv tool install ipython

# Install DuckDB
RUN curl https://install.duckdb.org | sh

# Set ownership
RUN sudo chown -R dev:dev /home/dev /app

# Create workspace
RUN sudo mkdir -p /workspace && sudo chown dev:dev /workspace

# Prevent future Python downloads and make tools available
ENV UV_PYTHON_DOWNLOADS=never

# For devcontainer
WORKDIR /workspace

# Expose ports
EXPOSE 1313 1314 3007

SHELL ["/bin/zsh", "-c"]
CMD ["/bin/zsh"]
