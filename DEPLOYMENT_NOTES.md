# ShopEase Protected Benchmark - Deployment Notes

## Production URL

```
https://shopease-protected.antester.com/
```

DNS A record required: `shopease-protected.antester.com → 3.7.14.72`
SSL: run `sudo certbot --nginx -d shopease-protected.antester.com` after DNS propagates.

## Server Architecture

- EC2: `ubuntu@3.7.14.72` (same instance as Antester)
- App lives at: `/home/appuser/shopease-protected` (cloned from this repo)
- Runs as: `appuser`, port `8081`
- Main Antester app unchanged at port `8000`

## Services

```
systemd: shopease-protected.service
nginx:   /etc/nginx/sites-available/shopease-protected
logs:    /var/log/shopease-protected.log
```

## Deployment Commands (what was run)

```bash
# 1. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Clone repo
sudo -u appuser git clone https://github.com/Pratham07411470/shopease-benchmark.git \
  /home/appuser/shopease-protected

# 3. Systemd service (written to /etc/systemd/system/shopease-protected.service)
sudo systemctl daemon-reload
sudo systemctl enable shopease-protected
sudo systemctl start shopease-protected

# 4. nginx config (written to /etc/nginx/sites-available/shopease-protected)
sudo ln -sf /etc/nginx/sites-available/shopease-protected \
            /etc/nginx/sites-enabled/shopease-protected
sudo nginx -t && sudo systemctl reload nginx

# 5. SSL (run after DNS A record propagates)
sudo certbot --nginx -d shopease-protected.antester.com
```

## systemd Unit File

```ini
[Unit]
Description=ShopEase Protected Benchmark
After=network.target

[Service]
User=appuser
WorkingDirectory=/home/appuser/shopease-protected
Environment="PORT=8081"
ExecStart=/usr/bin/node protected-server.js
Restart=always
RestartSec=5
StandardOutput=append:/var/log/shopease-protected.log
StandardError=append:/var/log/shopease-protected.log

[Install]
WantedBy=multi-user.target
```

## nginx Config Block

```nginx
server {
    listen 80;
    server_name shopease-protected.antester.com;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
(Certbot adds the SSL block automatically after `certbot --nginx`.)

## Route Verification (localhost:8081)

All routes verified before nginx:

| Route | Expected | Actual |
|-------|----------|--------|
| `/scenario/403` | 403 | 403 |
| `/scenario/429` | 429 + Retry-After | 429 |
| `/scenario/captcha` | 403 | 403 |
| `/scenario/challenge` | 503 | 503 |
| `/scenario/login` | 401 | 401 |
| `/scenario/blank` | 403 | 403 |
| `/?tester_access=allow` | 200 | 200 |
| `/protected.html` (no allowlist) | 403 | 403 |

## Demo URLs for Antester Frontend

| Demo | URL |
|------|-----|
| Buggy ecommerce | `https://pratham07411470.github.io/shopease-benchmark/` |
| Protected ecommerce (static JS wall) | `https://shopease-protected.antester.com/protected.html` |
| Protected ecommerce (owner-approved) | `https://shopease-protected.antester.com/?tester_access=allow` |

## Why This Demo Exists

Users ask: "What happens if my website has bot protection, CAPTCHA, WAF, or rate
limiting?" This demo answers that question live, without the user needing their
own protected site.

**Blocked flow** — run Antester against `/protected.html`:
Expected result: Antester reports access protection and recommends the site owner
allowlist the tester IP, provide a staging bypass token, or share test credentials.
It does NOT file the blocker pages as ShopEase product bugs.

**Owner-approved flow** — run Antester against `/?tester_access=allow`:
Expected result: Antester reaches the real ShopEase pages and tests them normally.

This proves: "Protected site? Antester will tell you what access is needed.
Once you authorize it, Antester tests normally."

## Updating the Deployment

```bash
ssh -i <key> ubuntu@3.7.14.72
sudo -u appuser bash -c 'cd /home/appuser/shopease-protected && git pull origin main'
sudo systemctl restart shopease-protected
```

## What This Does NOT Do

- Does not bypass, circumvent, or interact with real third-party WAFs
- Does not test Cloudflare, AWS WAF, Imperva, or any external access control
- All protection simulation is handled by this server's own logic
- The `?tester_access=allow` parameter only unlocks this benchmark's own gate,
  simulating what an owner does when they authorize a tester
