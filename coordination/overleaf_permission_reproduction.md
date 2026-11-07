# Browser permission reproduction and supported recovery

Checked 7 November 2026. This is a local diagnostic record, not a posted support report.

Observed on this Windows machine:

- The supported browser tool discovers both the Edge and Chrome extensions and lists an Overleaf tab.
- Selecting that tab is rejected before page content is returned, with the saved-site-permission/managed-policy denial.
- The user reports removing the Codex site blocking rule. A subsequent supported check still returned the same denial.
- A fresh Chrome extension connection also returned the same denial. No upload, edit or compilation took place during those checks.
- The approved source ZIP and raw CFD evidence remain preserved. Shell access and available disk space do not establish browser permission.

Public reports with similar symptoms, not proof of the same local cause:

- https://github.com/openai/codex/issues/55829 — Windows Chrome read-only access remains denied after visible Always allow.
- https://github.com/openai/codex/issues/56028 — Windows per-session origin denial persists after Always allow and restart.
- https://github.com/openai/codex/issues/56417 — visible site permission and effective saved denial disagree.

The subsequent read-only local check confirmed a stored conflict for the exact Overleaf origin: the global setting lists it as allowed and not denied, whereas this conversation lists it as denied and not allowed. This is direct local evidence of conflicting stored scope, not a claim about how the original denial arose. No permission file was modified. The runtime refusal remains the authoritative observation; a supported fresh-chat test must independently pass its own access check.

Installed packages queried read-only: OpenAI.Codex 26.1103.4239.0; OpenAI.ChatGPT-Desktop 1.2026.190.0. Package versions alone do not establish which authorization store or policy has priority.

Official recovery sequence: https://learn.chatgpt.com/docs/chrome-extension

1. Confirm the exact Overleaf host is absent from the desktop app's blocked-site list, and use the Chrome profile with the connected extension.
2. Restart browser/application if not yet done; keep the signed-in Overleaf project and saved source.
3. Start a genuinely new chat and perform one explicitly authorised, read-only @Chrome test of the existing Overleaf page. This is an official connection-state diagnostic, not an assurance that the permission is repaired. A denied test must stop rather than switch to bypass channels.
4. If the new-chat test succeeds, continue from the saved project/source; record the changed context. If it also fails, check supported app/extension updates and send /feedback with versions, exact denial, and a minimal reproduction.

No private browser permission stores, signed authorization state, browser-service code, security controls or raw CDP channels were edited or used to evade the denial. No public issue/comment was sent on the user's behalf.

For immediate coursework completion when automation remains blocked, the user can upload the reviewed source to the already approved Overleaf project, compile there, and save the PDF locally for independent page-by-page inspection. This preserves the user's Overleaf-only compilation requirement; a source preflight does not certify the rendered document.
