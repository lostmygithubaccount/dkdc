# Get my deployment working

I have root access to a DigitalOcean server at $VPS_IP. You can run commands with `ssh root@$VPS_IP` as needed.

Yesterday, we were working on deployment scripts. See ARCHITECTURE.md and other Markdown files for details, alongside the actual code. The script would fail in the middle of deploying on our server.

## Think through the solution

Start by taking a step back, analyzing our code and where things are at, and think through how to accomplish the goal. We want:

- https://dkdc.dev
- https://dkdc.io
- https://app.dkdc.io

All up and running. These work fine locally, we're just dealing with getting everything up and running on the server with SSL certificates and such.

Also note DNS is configured and already pointing at the IP address. You can use `dig` to see that.

## Working

Work through the feedback loop. First review the code here and make edits. Then get the server up and running. You'll confirm this w/ curl or similar on the live website until it's up and running as expected.

This might take a while. Work as a principal SRE and DevOps engineer to get this done as it's critical to have these services up today.

You're free to update the code. Do not make any `git` commits; just get everything working and I'll review/give feedback from there. Be careful not to run anything that requires user input or stdin or TTY and such.
