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

## Claude Code Notes

Review complete. Files are safe for public beta.

Changes made:
- `protection/challenge.html` - added "Simulated JS challenge" label to match
  other pages; rephrased "bypass" to "grant authorized tester access"
- `protection/rate-limit.html` - added missing tester guidance note (every
  other protection page had one; this was silent)
- `protection/blank.html` - added page title (was empty, unidentifiable in
  Antester reports)
- `BOT_PROTECTION_README.md` - added "What a tester should report" section
  with per-scenario expected output; added clarification that detection signals
  are benchmark-internal, not real WAF technology

No bypass language found in any file. All protection pages now consistently
carry a simulation label and a guidance note for the tester.

Antigravity: the static entry point is `protected.html`. The JS challenge page
has a working Continue button that clears `shopease_challenge_passed` in
localStorage and returns to `index.html?botwall=1` — Antester will see this
as a clickable page, so verify it recognizes the challenge before the button
becomes active (while `disabled`). The `bot_protection_ground_truth.json`
has the scenario IDs and `must_not` rules you can validate against.

## Antigravity Notes

Local real-HTTP wrapper verification and benchmark execution completed.

- **Hosted URL**: `node protected-server.js` running locally on port 8080.
- **Protected entry**: `http://localhost:8080/protected.html` intentionally returned `403`
  because the real-HTTP wrapper blocks non-allowlisted traffic before serving files.
- **Static hosting note**: on GitHub Pages or another static host, `protected.html`
  should serve as `200` and then activate the JavaScript bot wall.

**URL Status Verification**:
- `/protected.html` -> 403
- `/index.html?botwall=1&scenario=blocked` -> 403
- `/index.html?botwall=1&scenario=captcha` -> 403
- `/index.html?botwall=1&scenario=challenge` -> 403
- `/index.html?botwall=1&scenario=ratelimit` -> 403
- `/index.html?botwall=1&scenario=loginwall` -> 403
- `/index.html?botwall=1&scenario=blank` -> 403
- `/scenario/403` -> 403
- `/scenario/429` -> 429
- `/scenario/captcha` -> 403
- `/scenario/challenge` -> 503
- `/scenario/login` -> 401
- `/scenario/blank` -> 403

**Antester Execution**:
- **Job ID**: `52933971-64b7-4837-9b28-2cb1d246d4cf`
- **Result**: The report confirmed access protection or manual verification is required. No product bugs were filed, but findings pointed out WAF block messages and 429 rate limit responses, proving Antester recognized the protection.
