# Letting Claude drive your real Chrome

This makes a **locally-running Claude Code** control your **already-logged-in Chrome** (your cookies,
your sessions) via the Playwright MCP server.

> This does **not** work from the cloud / web Claude session — that one runs in an isolated container
> with no route to your Mac. Browser control only works with Claude Code running **on your Mac**.

## One-time setup (Mac)

### 1. Install Node + Claude Code
```bash
# Node 18+ (via Homebrew)
brew install node

# Claude Code CLI
npm install -g @anthropic-ai/claude-code
```

### 2. Get the repo on your Mac
```bash
git clone https://github.com/yanivshellbe/yanivshellbe.git
cd yanivshellbe
git checkout claude/algo-trading-system-t3MC0
```
The repo already ships `.mcp.json` (registers Playwright MCP) and the `browser-pilot` skill.

## Each session

### 3. Start Chrome with remote debugging
Quit all Chrome windows first (otherwise the profile is locked), then:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```
This Chrome uses your **default profile**, so you're already logged into Hetzner / DigitalOcean /
GitHub / Alpaca. Log into anything you still need.

> Prefer to keep your everyday Chrome separate? Use a dedicated profile:
> ```bash
> /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
>   --remote-debugging-port=9222 --user-data-dir="$HOME/ChromeDebugProfile"
> ```
> You'll log into sites once in that profile; it persists across sessions.

### 4. Run Claude Code in the repo
```bash
cd yanivshellbe
claude
```
On first run it will **prompt to trust the project MCP server** from `.mcp.json` — approve it.
(Reset later with `claude mcp reset-project-choices`.)

### 5. Ask it to drive the browser
```
/browser-pilot
> Provision the DigitalOcean droplet per deploy/cloud-init.yaml and report the IP.
```
or just describe the task — the skill auto-triggers on browser requests.

## Verify it's connected
Ask: *"Snapshot the current Chrome tab and tell me the page title."*
If it reads your real tab, you're wired up. If it errors with connection refused, Chrome isn't running
with `--remote-debugging-port=9222` (redo step 3).

## Safety notes
- The `browser-pilot` skill is instructed to **confirm before paid/destructive/irreversible actions**
  and to **never read credentials, 2FA codes, or password fields**.
- Remote debugging on port 9222 is **localhost-only** by default — don't expose that port to the
  internet or anyone on your network could drive your logged-in browser.
- Close the debugging Chrome when you're done.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `connect ECONNREFUSED 127.0.0.1:9222` | Chrome not started with the debug flag, or it's a different port. Redo step 3. |
| "profile is already in use" | Quit all Chrome windows, or use the `--user-data-dir` variant. |
| MCP tools don't appear in `claude` | You skipped the trust prompt; run `claude mcp reset-project-choices` and restart `claude`. |
| `npx` slow on first call | It's fetching `@playwright/mcp`; subsequent runs are cached. |
