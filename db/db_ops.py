import sqlite3
import json
from pathlib import Path
from db.encryption import encrypt_data, decrypt_data

DB_PATH = Path(__file__).parent / "audit_log.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent_name TEXT,
            action TEXT,
            encrypted_details TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pr_number TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mermaid_graph TEXT,
            trace_logs TEXT,
            audit_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def clear_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM audit_logs")
    conn.commit()
    conn.close()

def log_audit_action(agent_name: str, action: str, details: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    details_str = json.dumps(details)
    encrypted_details = encrypt_data(details_str)
    cursor.execute(
        "INSERT INTO audit_logs (agent_name, action, encrypted_details) VALUES (?, ?, ?)",
        (agent_name, action, encrypted_details)
    )
    conn.commit()
    conn.close()

def get_audit_logs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        log = dict(row)
        try:
            log['details'] = json.loads(decrypt_data(log['encrypted_details']))
        except Exception:
            log['details'] = {"error": "Failed to decrypt"}
        del log['encrypted_details']
        logs.append(log)
    return logs

def save_workflow_history(pr_number: str, mermaid_graph: str, trace_logs: str, audit_json: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workflows (pr_number, mermaid_graph, trace_logs, audit_json) VALUES (?, ?, ?, ?)",
        (pr_number, mermaid_graph, trace_logs, audit_json)
    )
    conn.commit()
    conn.close()

def get_workflow_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, pr_number, timestamp FROM workflows ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_workflow_by_id(wf_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workflows WHERE id = ?", (wf_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

init_db()
