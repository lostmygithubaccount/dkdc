# Claude Code in DevContainer

This devcontainer is configured to run Claude Code with authentication properly set up.

## Authentication Issue Resolved

Claude Code has two authentication modes:
1. **Interactive mode** (default): Uses OAuth flow, requires browser access
2. **Prompt mode** (`-p` flag): Can use `ANTHROPIC_API_KEY` environment variable

In a devcontainer, the OAuth flow doesn't work well since it requires browser access. The solution:

### The Wrapper Script

The `claude-wrapper.sh` script automatically:
- Uses `--dangerously-skip-permissions` for interactive mode (since OAuth isn't available in containers)
- Allows normal operation for prompt mode (which works with `ANTHROPIC_API_KEY`)

### Setup Requirements

1. Create `.devcontainer/.env` with your API keys:
```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

2. Ensure your host machine has the following files/directories that get mounted:
- `~/.claude/` - Claude configuration directory
- `~/.claude.json` - Claude settings
- `~/.config/` - General config directory
- Other config files as specified in `devcontainer.json`

### Usage

Once in the container:
```bash
# Interactive mode (uses --dangerously-skip-permissions automatically)
claude

# Prompt mode (uses ANTHROPIC_API_KEY)
claude -p "your prompt here"

# AI alias also works
ai
```

### Security Note

The `--dangerously-skip-permissions` flag bypasses Claude's permission system. This is acceptable in a devcontainer environment where:
- The container is isolated
- You control what files are accessible
- The container can be destroyed and recreated easily

### Mounted Directories

The devcontainer mounts several directories from your host:
- Auth configs: `~/.claude`, `~/.config`
- Shell configs: `~/.zprofile`, `~/.bash_aliases`, `~/.tmux.conf`
- Development tools: `~/.ipython`, `~/.codex`
- Workspace: `~/code/ascend-io` → `/workspaces`