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

# Copy project files as root (for docker-compose services)
WORKDIR /app
COPY . /app

# Switch to dev user for remaining setup
USER dev
WORKDIR /home/dev

# Set up fnm environment
ENV FNM_DIR="/home/dev/.fnm"
ENV PATH="/usr/local/bin:$PATH"

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

# Install Python development tools
RUN uv tool install ruff && \
    uv tool install pytest && \
    uv tool install ranger-fm && \
    uv tool install pre-commit && \
    uv tool install ipython

# Install DuckDB
RUN curl https://install.duckdb.org | sh

# Set ownership
RUN sudo chown -R dev:dev /home/dev

# Create workspace
RUN sudo mkdir -p /workspace && sudo chown dev:dev /workspace

# For devcontainer
WORKDIR /workspace

# Expose ports
EXPOSE 1313 1314 3007

SHELL ["/bin/zsh", "-c"]
CMD ["/bin/zsh"]