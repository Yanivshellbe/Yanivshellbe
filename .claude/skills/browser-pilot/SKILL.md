---
name: browser-pilot
description: Drive the user's already-logged-in Chrome via the Playwright MCP server to complete web tasks (cloud provisioning, form filling, dashboard checks, scraping a value). Use when the user asks Claude to "use my browser", "do it in Chrome", provision/click through a web console, or read something from a logged-in page. Requires local Claude Code + Chrome started with --remote-debugging-port=9222.
---

# Browser Pilot

You can control the user's real Chrome (with their existing logins/cookies) through the
**Playwright MCP** tools, which connect to a Chrome instance running with remote debugging.

## Preflight — confirm the connection before acting

1. The Playwright MCP server is registered in `.mcp.json` with `--cdp-endpoint=http://localhost:9222`.
   It attaches to an existing Chrome; it does **not** launch a clean one. If the tools error with a
   connection refused, the user hasn't started Chrome with remote debugging — stop and tell them to run:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   ```
   (Quit all existing Chrome windows first, or the profile will be locked.)
2. Take a snapshot (accessibility tree) of the current page before doing anything, so you know what's
   on screen and operate on the real DOM rather than guessing coordinates.

## Operating principles

- **Snapshot, then act.** Prefer the structured accessibility snapshot over screenshots for finding
  elements; use screenshots only to confirm visual state or when the snapshot is ambiguous.
- **One action, then re-observe.** After every navigation/click/type, re-snapshot before the next step.
  Pages change; stale element refs cause misclicks.
- **Never assume success.** Read the page back to confirm the result (URL changed, success toast,
  expected text present) before reporting done.
- **Announce destructive/irreversible/paid actions and get explicit confirmation first** — creating
  paid cloud resources, changing repo visibility, deleting anything, submitting payments, sending
  messages. State exactly what you're about to click and the cost, then wait for a yes.
- **Stay on task.** Don't navigate to unrelated sites. Don't read or exfiltrate credentials, password
  fields, 2FA codes, or unrelated logged-in data. If a task needs a secret, ask the user to enter it
  themselves in the browser.
- **Respect guardrails in the request.** If the user sets a budget ceiling or a "stop and ask if X",
  honor it literally.

## Typical playbook: provision a cloud server

1. Snapshot the current page; confirm you're logged into the right console.
2. Navigate to the create-resource page.
3. Fill fields one at a time (region, image, size, name), re-snapshotting between major steps.
4. For a long config/user-data textarea, type or paste the full block, then snapshot to verify it
   landed intact (check the first and last lines).
5. **Before the final "Create / Buy" click:** restate region + size + monthly price + name, and confirm
   it's within any budget the user gave. If over budget or ambiguous, stop and ask.
6. After creation, read back the resource's IP/status and report it verbatim.

## What to report

Plain text: the concrete result (IP address, status, URL, the value you read), and any place you
stopped for confirmation. If something failed, report the exact error text from the page, not a guess.
