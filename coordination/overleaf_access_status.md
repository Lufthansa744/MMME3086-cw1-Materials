# Overleaf access status

Project: https://www.overleaf.com/project/6aed174c208587f797ee667b

The approved source was downloaded successfully before the later access block and is preserved under `report/overleaf_original`. The Google sign-in succeeded in the in-app browser; the user also confirmed signing in through Edge.

Subsequent browser access was rejected by the origin permission gate: a saved user permission or managed policy blocks observation of https://www.overleaf.com. The user expressly renewed permission in chat, but the saved gate still rejected access. Native Edge automation separately stopped because it could not reliably identify the current browser URL. Neither error establishes a Google or Overleaf network outage.

No blocked browser action has been retried through raw HTTP sessions, alternate automation frameworks, browser internals or other policy workarounds. Local report source and graphics continue to be prepared; no local LaTeX compilation is performed.

Official guidance checked on 7 November 2026:

- Built-in browser: Settings > Browser > Agent permissions; inspect website-specific rules: https://learn.chatgpt.com/docs/browser
- Connected browser: Settings > Computer Use > Manage beside the browser. Remove the website from the blocklist so permission can be requested again: https://learn.chatgpt.com/docs/chrome-extension

The user must change any saved blocking setting or resolve an administrator restriction. Once authorised browser access actually works, upload the prepared source/assets, compile only in Overleaf, inspect every final page and resolve errors, warnings, overflows and page-count issues before calling the report submission-ready.

Latest recheck: Edge extension connected successfully and the approved project is visible in its tab inventory. An actual page-observation request was still explicitly rejected by the saved origin permission gate. After a later extension reconnection, inventory confirms the project remains open; no repeated page observation is attempted until the blocking rule changes. Browser connection alone does not verify read/edit/compile access.

After the user explicitly confirmed removing the Codex site blocking rule, a fresh observation of the approved project in the reconnected Edge session was attempted. It was again rejected by the origin gate with the same saved-permission/managed-policy reason. No upload/edit/compile was performed and no alternate route was used. The permission change has not become effective for this connection.

Further diagnostic on 7 November: a fresh Edge connection showed the Overleaf projects tab, but the origin gate again denied observation. Official extension troubleshooting confirms a desktop-app restart/new-chat diagnostic after blocklist checks. Desktop app UI automation is disallowed by the Computer Use skill; the restart was handed to the user. No browser-policy files or security settings were edited. Final ZIP members were compared byte-for-byte with the reviewed prepared source and iCloud snapshot.
