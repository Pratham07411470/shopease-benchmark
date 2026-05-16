# Multi-Agent Launch Handoff

We are working together on the Antester controlled-beta launch. Codex is handling
the ShopEase protected benchmark implementation and code sanity checks. Claude
Code should review product trust language and QA credibility. Antigravity should
handle hosting/deployment verification and benchmark execution.

## Shared Goal

Make the protected ShopEase benchmark useful for validating that Antester handles
bot protection, CAPTCHA, rate limits, login walls, and allowlist flows correctly.
The expected behavior is detection and clear owner guidance, not bypassing.

## Claude Code Prompt

You are collaborating with Codex and Antigravity on the Antester launch. Review
`C:\Users\prath\Work\Others\benchmark\shopease-benchmark` after Codex's protected
benchmark changes.

Your tasks:
- Review `BOT_PROTECTION_README.md`, `protection/*.html`, and blocker copy.
- Make the language professional, calm, and safe for public beta.
- Ensure it never implies Antester bypasses Amazon, Flipkart, Cloudflare, WAFs,
  CAPTCHAs, or third-party access controls.
- Ensure the expected user action is owner-approved access: IP allowlist, staging
  bypass token, trusted header, or test credentials.
- Confirm the normal `index.html` benchmark remains usable and the protected flow
  starts from `protected.html`.
- If you edit files, commit with a concise message and note changed paths.

Acceptance criteria:
- Copy is clear to QA leads and PMs.
- No provider/internal implementation details.
- No bypass language.
- Static protected pages still load without a build step.

## Antigravity Prompt

You are collaborating with Codex and Claude Code on the Antester launch. Codex
implemented the ShopEase protected benchmark. Your job is deployment and proof.

Your tasks:
- Host `C:\Users\prath\Work\Others\benchmark\shopease-benchmark` quickly.
- Test static mode using `protected.html`.
- If hosting on EC2, run `node protected-server.js` to test real HTTP statuses.
- Verify these URLs render or return expected statuses:
  `/protected.html`
  `/index.html?botwall=1&scenario=blocked`
  `/index.html?botwall=1&scenario=captcha`
  `/index.html?botwall=1&scenario=challenge`
  `/index.html?botwall=1&scenario=ratelimit`
  `/index.html?botwall=1&scenario=loginwall`
  `/index.html?botwall=1&scenario=blank`
  `/scenario/403`
  `/scenario/429`
- Run Antester against the protected URL and confirm the report says access
  protection or manual verification is required, not product bugs.
- Record final URLs, commands, status codes, and benchmark result in a handoff
  note or commit.

Acceptance criteria:
- Static protected entry works.
- Real server mode returns true `403`, `429`, `401`, and `503` where applicable.
- Antester produces owner-guidance language instead of bypass attempts.

## Codex Notes

Codex added:
- `protected.html`
- `protection/bot-protection.js`
- `protection/blocked.html`
- `protection/captcha.html`
- `protection/challenge.html`
- `protection/rate-limit.html`
- `protection/login-wall.html`
- `protection/blank.html`
- `protection/allowlist.html`
- `protected-server.js`
- `BOT_PROTECTION_README.md`

Normal benchmark URL remains `index.html`. Protected static entry is
`protected.html`. Real HTTP benchmark entry is `node protected-server.js`.
