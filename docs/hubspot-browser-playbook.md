# HubSpot browser playbook (checklists)

Use with **cursor-ide-browser**: always **`browser_snapshot` → ref → one action → snapshot** after navigation or DOM change. Steps are **logical**; HubSpot’s DOM changes — use search, nav, and filters rather than fixed selectors.

Assumptions: Sales/Service Hub Professional, `https://app.hubspot.com/`, user completes login/2FA when prompted.

---

## 1. Open Global Search and find a contact by email

1. `browser_navigate` to `https://app.hubspot.com/` (or stay on current app route).
2. `browser_snapshot` — locate **global search** (often top bar).
3. Click search ref → type email substring → `browser_wait_for` for results.
4. `browser_snapshot` — choose contact result ref → `browser_click`.
5. Confirm contact record: `browser_snapshot` (and screenshot if useful).

## 2. Open a contact from Contacts index (filter path)

1. Navigate via left nav: **Contacts** → **Contacts** (wording may vary).
2. `browser_snapshot` — find **search/filter** for email or name.
3. Apply filter / type → wait for table refresh.
4. `browser_snapshot` — click row or primary name link.
5. Verify record header in new snapshot.

## 3. Create a task on a contact

1. Open contact record (checklist 1 or 2).
2. `browser_snapshot` — find **Task** / **Create task** / activity area.
3. One action per snapshot: open composer → fill title → due date → assignee if needed.
4. Save → `browser_wait_for` success or activity list update → snapshot to confirm.

## 4. Add contact to a static list

1. Open contact record.
2. `browser_snapshot` — find **List memberships** / **Add to list** (or **Actions** menu).
3. Click → search list name → select → confirm.
4. Snapshot to verify membership.

## 5. Open Deals and filter by pipeline / owner

1. **Sales** → **Deals** (or **CRM** → **Deals** per nav).
2. `browser_snapshot` — open **view** / **filter** / **pipeline** controls.
3. Set pipeline, owner, or stage filters one control at a time.
4. Snapshot table; optional screenshot for stakeholder.

## 6. Open a specific deal card

1. From Deals index (checklist 5), use search or filters to narrow.
2. Click deal name link → snapshot deal record.

## 7. Open Sequences (enrollment)

1. Navigate to **Automation** → **Sequences** (exact path varies by hub).
2. `browser_snapshot` — locate target sequence → open.
3. For enroll: use **Enroll** / contact picker — **confirm destructive/mass enroll** with user before executing.

## 8. Open a workflow (edit mode)

1. **Automation** → **Workflows**.
2. Filter by name if available → click workflow.
3. For **edit**: snapshot before clicking **Edit** — confirm with user if workflow is live.

## 9. Settings: object / property configuration

1. **Settings** (gear) → search setting name (e.g. **Properties**).
2. Choose object (Contacts/Companies/Deals/Tickets).
3. One field or toggle per action; save → wait → snapshot.

## 10. Inbox / conversations (Service)

1. **Conversations** / **Inbox** from nav.
2. Filter channel / status via UI → open thread.
3. Reply flows may cross **iframes**; if tools cannot see inner content, stop and use HubSpot UI manually or Conversations API where supported.

---

## Blockers (stop and hand to human)

- Captcha, SSO window, or **session expired** screen.
- **2FA** prompt not yet completed.
- Blank loading or repeated errors: capture `browser_console_messages` + `browser_network_requests`, then user retry or API path.

---

## When to skip the browser

- Bulk property updates, imports, exports: **Private App + scripts** (`scripts/op_run.sh`).
- Project upload/deploy: **`hs`** from `hubspot-internal-app` per package scripts.
- Auditable repeat jobs: **API**, not UI clicks.
