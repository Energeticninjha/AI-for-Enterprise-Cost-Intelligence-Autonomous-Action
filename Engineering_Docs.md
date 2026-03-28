# AvataarFlow: Engineering Overview & Architecture Documentation 

## 1. System Abstract
AvataarFlow is an autonomous, multi-agent AI framework designed specifically for "Contract-to-Payment" procurement orchestration and designed for ET AI Hackathon 2026. Leveraging LangGraph, deterministic tool boundaries, and self-healing algorithms, the system minimizes human intervention while enforcing strict financial and statutory (Indian-context) compliance.

## 2. Architecture & Core Components
### 2.1 Multi-Agent Engine (LangGraph)
The core orchestration uses `LangGraph` to manage state transitions asynchronously across 7 highly specialized agent nodes located in the `/agents` directory:

- **Intake Agent:** Parses incoming PDFs (using `tools.pdf_parser`) and populates the initial PR data object and metadata.
- **Sourcing Agent:** Validates internal/external vendor budget heuristics, vendor catalog data, and optimization metrics.
- **Contract Agent:** Responsible for statutory verifications. Executes `tools.india_validators.py` for GST/PAN checksum and format integrity. Capable of raising exceptions to halt the workflow and routing to self-healing node.
- **Exception Agent:** Receives failed states (like missing PAN strings or mismatched GST schemas) and attempts to self-heal corrupted data using logic and metadata context extraction before routing back to the Contract Agent for re-validation.
- **Approval Agent:** The primary human-in-the-loop interlock. Programmatically stalls the workflow when financial constraints (e.g., transactions exceeding 1,000,000 INR) are breached, awaiting a frontend override.
- **Execution Agent:** Performs the final 3-way match mechanism (PR, PO, Invoice) and fires HTTP REST payloads to the Mock ERP backend via `tools.erp_client`.
- **Audit Agent:** Seals the graph execution, generating an immutable cryptographic trail of the entire workflow.

### 2.2 Shared Execution State (`GraphState`)
Defined in `agents/state.py`, a centralized `TypedDict` acts as the single source of truth passed synchronously between nodes. It contains context definitions:
- `pr_id`, `po_id`, `invoice_id`, `vendor_id`, `amount`
- `pdf_path`, `pr_data`, `issues`
- `status` and `approval_status` (controlling critical edge logic conditions for human loops)

### 2.3 Mock ERP Backend (`FastAPI`)
Hosted independently via Uvicorn/FastAPI out of `/mock_erp/main.py`, exposing autonomous simulation endpoints reflecting traditional procurement systems:
- `POST /pr`: Generates and reconciles PR strings.
- `POST /po`: Generates canonical Purchase Orders.
- `POST /invoice`: Triggers a basic validation format against existing PRs and POs and executes theoretical payment routing.

### 2.4 Secure Audit Vault & Data Storage (`SQLite`)
- **`audit_log.db`**: Subsystem state tracking maintained by `/db/db_ops.py`.
- **AES-256 Encryption:** Scripts in `db/encryption.py` utilize symmetric Fernet keys (loaded from `.env`) to encrypt raw JSON payloads, agent reasoning contexts, and tool executions dynamically before database insertion to ensure rigid financial security compliance.
- **Historical Workflows Archiving:** Archives the structural `mermaid_graph`, logic strings (`live_trace.log`), and JSON footprint per graph run so deep visualization rewinds can occur continuously.

### 2.5 Real-time UI & Watcher Services
- **Dashboard (`app/dashboard.py`):** A frontend Streamlit application rendering an interactive dashboard tailored for Audit/Finance Officers. Key features include an actively ticking UI parsing a Live Reasoning Trace terminal, cryptographic payload decryptions, and downloadable certified PDF summaries generated via `fpdf`. 
- **Time-Travel Hydration:** Leverages the archived entries in the database to completely reconstruct previous agent trace logs and graph diagrams precisely as they executed.
- **Email/Local-Drop Watcher (`app/watcher_service.py`):** A daemonized system hook operating asynchronously to fetch new PDFs via unread IMAP server entries (`PROCUREMENT_PR` subjects), OR via local offline mocks dropped inside `/data/mail_inbox`. It kicks off the entire LangGraph suite headlessly.

## 3. Workflow Lifecycle (Typical Happy Path)
1. **Trigger Phase:** PDF Invoice/Quote dropped into `data/mail_inbox` (simulated queue) or directly fired via Streamlit side-panel test scenarios.
2. **State Init:** LangGraph instantiates with `vendor_id` and raw filesystem target mappings.
3. **Extraction & Hard Validation:** Intake & Sourcing sequence base variables. Contract Agent aggressively checks GST/PAN strings against the `india_validators`.
4. **Approval Loop Isolation:** Bypasses human validation logic cleanly under the monetary threshold limit.
5. **ERP Execution API Post:** The Execution Agent resolves the Graph payload and commits identical copies of the JSON via `/pr`, `/po`, and `/invoice` external API calls.
6. **DB Ledger Flush:** The persistent filesystem removes the `live_trace.log` memory, AES encrypts tool metadata, flushes to `audit_logs` and `workflows` records, and halts.

## 4. Disaster Recovery & Exceptions
AvataarFlow's state edge handling intelligently mitigates process blockades:
- **Sticky Self-Healing Exception:** If the *Exception Agent* attempts to rectify text identifiers and fails cyclically (`error_count` > recursive limit threshold), the LangGraph dynamically shuts down and flags isolated tracking anomalies.
- **Enforced Security Stalls:** Manual override parameters enforce process pauses gracefully so human administrators can dictate the `approval_status = "approved"` vector overriding standard ReAct autonomous flows.
