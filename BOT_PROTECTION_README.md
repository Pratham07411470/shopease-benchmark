# ShopEase Protected Benchmark

This benchmark keeps the original ShopEase planted bugs intact and adds a
separate access-protection layer for testing how Antester handles protected
sites.

## Static mode

Use this when hosting on GitHub Pages or any static host:

```text
https://your-host/shopease-benchmark/protected.html
```

`protected.html` enables a session bot wall and redirects into the normal site.
The normal root `index.html` remains the original bug-finding benchmark.

Useful scenarios:

```text
index.html?botwall=1&scenario=blocked
index.html?botwall=1&scenario=captcha
index.html?botwall=1&scenario=challenge
index.html?botwall=1&scenario=ratelimit
index.html?botwall=1&scenario=loginwall
index.html?botwall=1&scenario=blank
index.html?botwall=reset
index.html?botwall=1&tester_access=allow
```

Expected tester behavior: detect access protection, explain the blocker, and
suggest owner-approved access such as IP allowlisting or a staging bypass token.
It should not treat the blocker as a product bug and should not try to bypass
third-party protection.

## Real HTTP mode

Static hosting cannot return true HTTP 403 or 429 responses. For protocol-level
testing on EC2:

```bash
node protected-server.js
```

Optional environment:

```bash
PORT=8080
ALLOWLIST_IPS=3.7.14.72
TEST_ACCESS_TOKEN=owner-approved-token
```

Routes:

```text
/scenario/403
/scenario/429
/scenario/captcha
/scenario/challenge
/scenario/login
/scenario/blank
/?tester_access=allow
```

To simulate authorized owner access, either add the tester IP to
`ALLOWLIST_IPS`, pass `?tester_access=allow`, or send header:

```text
x-shopease-test-access: owner-approved-token
```
