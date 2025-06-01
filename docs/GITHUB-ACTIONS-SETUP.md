# GitHub Actions Setup for Auto-Deployment

This guide helps you set up automatic deployment whenever you push to the main branch.

## Prerequisites

- Your VPS is already set up with the initial deployment
- You have SSH access to your VPS as root
- You have admin access to your GitHub repository

## Setup Steps

### 1. Generate an SSH Key for GitHub Actions

On your VPS:

```bash
# Generate a new SSH key specifically for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy -N ""

# Add the public key to authorized_keys
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys

# Display the private key (you'll need this for GitHub)
cat ~/.ssh/github_actions_deploy
```

### 2. Add Secrets to GitHub

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:

   - **VPS_HOST**: Your server's IP address or hostname
   - **VPS_SSH_KEY**: The private key content from step 1 (entire content including BEGIN/END lines)

### 3. Test the Workflow

1. Make a small change to any file
2. Commit and push to main branch
3. Go to Actions tab on GitHub to see the deployment running
4. Check your live sites to confirm the update

## How It Works

When you push to the main branch:
1. GitHub Actions connects to your VPS via SSH
2. Runs the update script which:
   - Pulls latest code from GitHub
   - Rebuilds static sites
   - Restarts dynamic services
3. Your sites are updated within ~1-2 minutes

## Manual Deployment

You can also trigger deployment manually:
1. Go to Actions tab
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Select main branch
5. Click "Run workflow" button

## Troubleshooting

### Deployment Fails

Check the GitHub Actions logs for errors. Common issues:
- SSH key not properly configured
- VPS_HOST secret not set correctly
- Server is down or unreachable

### Changes Not Appearing

1. Check if the workflow ran successfully
2. SSH to server and check logs: `cd /opt/dkdc && docker compose logs`
3. Manually run update: `cd /opt/dkdc && ./bin/update.sh`

## Security Notes

- The SSH key is only for deployment (no sudo access needed)
- Consider using a deployment-specific user instead of root
- Rotate SSH keys periodically
- Keep your GitHub secrets secure