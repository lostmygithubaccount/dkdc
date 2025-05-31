# DNS Setup Guide

## How DNS Routing Works

```
Internet Request: https://dkdc.dev
       ↓
DNS Resolution: dkdc.dev → YOUR_VPS_IP
       ↓
nginx (port 80/443): Routes internally to dkdc-dev:1313
       ↓
Response: Your website content
```

## Required DNS Records

### For DigitalOcean DNS:

1. **Go to Networking → Domains**
2. **Add domain: `dkdc.dev`**
3. **Create these A records:**
   ```
   Hostname: @     Will redirect to: YOUR_VPS_IP    TTL: 300
   Hostname: app   Will redirect to: YOUR_VPS_IP    TTL: 300
   ```

4. **Add domain: `dkdc.io`**
5. **Create A record:**
   ```
   Hostname: @     Will redirect to: YOUR_VPS_IP    TTL: 300
   ```

6. **Add domain: `dkdc.ai`**
7. **Create A record:**
   ```
   Hostname: @     Will redirect to: YOUR_VPS_IP    TTL: 300
   ```

### For Cloudflare:

1. **Add site: `dkdc.dev`**
2. **DNS Records:**
   ```
   Type: A    Name: dkdc.dev        Content: YOUR_VPS_IP    Proxy: OFF
   Type: A    Name: app.dkdc.dev    Content: YOUR_VPS_IP    Proxy: OFF
   ```

3. **Add site: `dkdc.io`**
4. **DNS Record:**
   ```
   Type: A    Name: dkdc.io         Content: YOUR_VPS_IP    Proxy: OFF
   ```

5. **Add site: `dkdc.ai`**
6. **DNS Record:**
   ```
   Type: A    Name: dkdc.ai         Content: YOUR_VPS_IP    Proxy: OFF
   ```

### Generic DNS Provider:

```
Record Type: A
Name/Host: @              Value: YOUR_VPS_IP
Name/Host: app            Value: YOUR_VPS_IP

For dkdc.io:
Name/Host: @              Value: YOUR_VPS_IP

For dkdc.ai:
Name/Host: @              Value: YOUR_VPS_IP
```

## Important Notes

**✅ What You Need:**
- Only the server IP address (e.g., `143.198.123.45`)
- A records pointing to that IP
- Wait 5-60 minutes for DNS propagation

**❌ What You DON'T Need:**
- Port numbers in DNS (e.g., `:80` or `:443`)
- CNAME records (use A records)
- Complex routing rules

**Why No Ports?**
- DNS only resolves domain names to IP addresses
- Web browsers automatically use port 80 (HTTP) or 443 (HTTPS)
- nginx running on your VPS listens on these standard ports
- nginx then routes internally based on domain name

## Testing DNS Setup

```bash
# Check if DNS is working
nslookup dkdc.dev
dig dkdc.dev

# Should return your VPS IP address
# Wait for propagation if it returns old/wrong IP

# Test HTTP connectivity (before SSL)
curl -I http://dkdc.dev
curl -I http://app.dkdc.dev
curl -I http://dkdc.io
curl -I http://dkdc.ai    # Should redirect to dkdc.io
```

## Common Issues

**DNS Not Resolving:**
- Wait longer (up to 24 hours max)
- Check TTL settings (lower = faster updates)
- Clear local DNS cache: `sudo dscacheutil -flushcache` (macOS)

**SSL Certificate Errors:**
- Only run SSL setup AFTER DNS is working
- Let's Encrypt validates domain ownership via DNS
- nginx must be running and accessible on port 80

**"This site can't be reached":**
- Check VPS firewall allows ports 80 and 443
- Verify nginx container is running: `docker compose ps`
- Check nginx logs: `docker compose logs nginx`

## VPS IP Address

**Find your VPS IP:**
```bash
# On DigitalOcean dashboard
# Or from inside VPS:
curl ifconfig.me
ip addr show
```

That's it! No ports, no complex routing - just point your domains to your server IP and nginx handles the rest. 🎯