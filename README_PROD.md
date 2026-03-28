# AvataarFlow Production Architecture

This document explains the **Phase 3** update, which replaces manual UI triggers with a 100% autonomous Event-Driven logic (Simulated Webhooks).

## Event-Driven Setup
1. **Inbox Monitoring**: `app/watcher_service.py` is an always-on background process that listens to the `data/mail_inbox` folder.
2. **Autonomous Triggering**: As soon as a PDF arrives via a webhook or mail drop, the `watcher_service` parses the file and instantiates a unique LangGraph execution thread (`run_avataar_flow`).
3. **Audit History Sync**: Once processed, files are archived to `data/processed_history` with a timestamp. The Streamlit dashboard stays completely synced using an auto-refresh toggle, acting strictly as a monitoring pane rather than an interactive start button.

## How to use:
- Run `python app/watcher_service.py` in the background.
- Drop a PDF into `data/mail_inbox/`.
- Watch the dashboard automatically pick up the real-time reasoning trace and add the file to the Audit History sidebar.
