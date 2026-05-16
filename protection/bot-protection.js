(function () {
  "use strict";

  const KEY_ENABLED = "shopease_botwall_enabled";
  const KEY_TRUSTED = "shopease_trusted_tester";
  const KEY_CHALLENGE = "shopease_challenge_passed";
  const KEY_VISITS = "shopease_recent_visits";
  const params = new URLSearchParams(window.location.search);
  const path = window.location.pathname.replace(/\\/g, "/");

  if (path.includes("/protection/")) return;

  if (params.get("botwall") === "reset") {
    [KEY_ENABLED, KEY_TRUSTED, KEY_CHALLENGE, KEY_VISITS].forEach((k) => localStorage.removeItem(k));
  }

  if (params.get("botwall") === "1") localStorage.setItem(KEY_ENABLED, "1");
  if (params.get("tester_access") === "allow") {
    localStorage.setItem(KEY_TRUSTED, "1");
    localStorage.setItem(KEY_CHALLENGE, "1");
  }
  if (params.get("botwall") === "0") localStorage.removeItem(KEY_ENABLED);

  const enabled = localStorage.getItem(KEY_ENABLED) === "1";
  const trusted = localStorage.getItem(KEY_TRUSTED) === "1";
  if (!enabled || trusted) return;

  const base = path.split("/").slice(0, -1).join("/") || ".";
  const go = (page, extra = "") => {
    window.location.replace(`${base}/protection/${page}${extra}`);
  };

  const forced = params.get("scenario");
  const forcedMap = {
    blocked: "blocked.html",
    captcha: "captcha.html",
    challenge: "challenge.html",
    ratelimit: "rate-limit.html",
    loginwall: "login-wall.html",
    blank: "blank.html"
  };
  if (forced && forcedMap[forced]) {
    go(forcedMap[forced], `?from=${encodeURIComponent(path)}`);
    return;
  }

  const now = Date.now();
  const visits = JSON.parse(localStorage.getItem(KEY_VISITS) || "[]")
    .filter((t) => now - t < 30000);
  visits.push(now);
  localStorage.setItem(KEY_VISITS, JSON.stringify(visits));

  if (visits.length > 7) {
    go("rate-limit.html");
    return;
  }

  const ua = navigator.userAgent || "";
  const automationSignals = [
    navigator.webdriver === true,
    /HeadlessChrome|Playwright|Puppeteer|Selenium|WebDriver/i.test(ua),
    navigator.plugins && navigator.plugins.length === 0,
    !navigator.languages || navigator.languages.length === 0
  ].filter(Boolean).length;

  if (automationSignals >= 2) {
    go("blocked.html");
    return;
  }

  if (!localStorage.getItem(KEY_CHALLENGE)) {
    go("challenge.html");
    return;
  }

  if (/dashboard|account|checkout|orders/i.test(path)) {
    go("login-wall.html");
  }
})();
