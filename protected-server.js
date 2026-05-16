/*
  Tiny real-HTTP wrapper for the ShopEase protected benchmark.

  Static hosting can show blocker pages, but it cannot return real 403/429
  responses. Run this on EC2 when you want protocol-level protection tests.

  Usage:
    node protected-server.js

  Optional env:
    PORT=8080
    ALLOWLIST_IPS=1.2.3.4,5.6.7.8
    TEST_ACCESS_TOKEN=owner-approved-token
*/
const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const ROOT = __dirname;
const PORT = Number(process.env.PORT || 8080);
const ALLOWLIST = new Set((process.env.ALLOWLIST_IPS || "").split(",").map(s => s.trim()).filter(Boolean));
const TEST_TOKEN = process.env.TEST_ACCESS_TOKEN || "shopease-owner-test";
const RATE_WINDOW_MS = 30000;
const RATE_LIMIT = 10;
const visits = new Map();

const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".svg": "image/svg+xml"
};

function clientIp(req) {
  const forwarded = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  return forwarded || req.socket.remoteAddress || "";
}

function isAllowed(req, url) {
  const ip = clientIp(req).replace(/^::ffff:/, "");
  if (ALLOWLIST.has(ip)) return true;
  if (url.searchParams.get("tester_access") === "allow") return true;
  if (req.headers["x-shopease-test-access"] === TEST_TOKEN) return true;
  return false;
}

function rateLimited(ip) {
  const now = Date.now();
  const list = (visits.get(ip) || []).filter(t => now - t < RATE_WINDOW_MS);
  list.push(now);
  visits.set(ip, list);
  return list.length > RATE_LIMIT;
}

function sendFile(res, rel, status = 200, headers = {}) {
  const target = path.resolve(ROOT, rel);
  const relative = path.relative(ROOT, target);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    res.writeHead(400);
    res.end("Invalid path");
    return;
  }
  fs.readFile(target, (err, body) => {
    if (err) {
      res.writeHead(404, {"content-type": "text/plain"});
      res.end("Not found");
      return;
    }
    res.writeHead(status, {"content-type": mime[path.extname(target)] || "application/octet-stream", ...headers});
    res.end(body);
  });
}

function scenario(req, res, name) {
  if (name === "429") return sendFile(res, "protection/rate-limit.html", 429, {"Retry-After": "120"});
  if (name === "captcha") return sendFile(res, "protection/captcha.html", 403);
  if (name === "challenge") return sendFile(res, "protection/challenge.html", 503, {"x-shopease-challenge": crypto.randomUUID()});
  if (name === "blank") {
    res.writeHead(403, {"content-type": "text/html; charset=utf-8"});
    res.end("");
    return;
  }
  if (name === "login") return sendFile(res, "protection/login-wall.html", 401);
  return sendFile(res, "protection/blocked.html", 403, {"x-shopease-waf": "blocked"});
}

http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const ip = clientIp(req).replace(/^::ffff:/, "");

  if (url.pathname.startsWith("/scenario/")) {
    return scenario(req, res, url.pathname.split("/").pop());
  }

  if (!isAllowed(req, url)) {
    if (rateLimited(ip)) return scenario(req, res, "429");
    return scenario(req, res, "403");
  }

  let rel = decodeURIComponent(url.pathname);
  if (rel === "/" || rel === "") rel = "/index.html";
  sendFile(res, rel.replace(/^\/+/, ""));
}).listen(PORT, () => {
  console.log(`ShopEase protected benchmark listening on http://localhost:${PORT}`);
});
