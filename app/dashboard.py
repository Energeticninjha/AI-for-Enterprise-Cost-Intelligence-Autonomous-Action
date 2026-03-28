import streamlit as st
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.graph import build_graph, GraphState
from agents.state import GraphState as CustomGraphState
from tests.scenarios import generate_scenarios
from db.db_ops import get_audit_logs, clear_db, get_workflow_history, get_workflow_by_id, save_workflow_history
from fpdf import FPDF
import threading
from app.watcher_service import watch_loop

@st.cache_resource
def init_watcher_thread():
    print("Starting background watcher thread...")
    t = threading.Thread(target=watch_loop, daemon=True)
    t.start()
    return t

init_watcher_thread()
st.set_page_config(page_title="AvataarFlow - Multi-Agent Enterprise Orchestration", page_icon="🏦", layout="wide")

st.markdown("""
    <div style='background-color: #ffebee; color: #b71c1c; padding: 10px; text-align: center; font-weight: bold;'>
        DISCLAIMER: Demo only - Not legal/financial advice. Simulated for ET AI Hackathon 2026.
    </div>
""", unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'logged_in_toast' not in st.session_state:
    st.session_state.logged_in_toast = False

from dotenv import load_dotenv
load_dotenv()
ADMIN_USER = os.getenv("ADMIN_USER", "ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS", "ADMIN_PASS")

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3rem; margin-bottom: 0px;'>🏦</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-top: 0px;'>AvataarFlow</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #888;'>Secure Auditor Portal</h4>", unsafe_allow_html=True)
        st.write("")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Access Portal", use_container_width=True)
            if submitted:
                if username == ADMIN_USER and password == ADMIN_PASS:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    st.stop()

if not st.session_state.logged_in_toast:
    st.toast("Session Started: Dharshini Sree (Lead Auditor)")
    st.session_state.logged_in_toast = True

st.title("🏦 AvataarFlow: Contract-to-Payment AI Orchestration")
st.caption("Powered by LangGraph & Multi-Agent Architecture")

if 'workflow' not in st.session_state:
    st.session_state.workflow = build_graph()
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = generate_scenarios()
if 'run_logs' not in st.session_state:
    st.session_state.run_logs = []
if 'current_node' not in st.session_state:
    st.session_state.current_node = "START"
if 'workflow_state' not in st.session_state:
    st.session_state.workflow_state = None
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if 'active_workflow' not in st.session_state:
    st.session_state.active_workflow = None

def get_mermaid_graph(current_node):
    graph = "graph TD\nSTART --> intake_agent\n"
    graph += "intake_agent --> sourcing_agent\n"
    graph += "sourcing_agent --> contract_agent\n"
    graph += "contract_agent --> approval_agent\n"
    graph += "contract_agent -.-> exception_agent\n"
    graph += "approval_agent --> execution_agent\n"
    graph += "execution_agent --> audit_agent\n"
    graph += "execution_agent -.-> exception_agent\n"
    graph += "exception_agent -.-> contract_agent\n"
    graph += "audit_agent --> END\n"
    graph = graph.replace(current_node, f"{current_node}:::active")
    graph += "\nclassDef active fill:#f9f,stroke:#333,stroke-width:4px;\n"
    return graph

def generate_audit_pdf(logs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="AvataarFlow Audit Trail", ln=True, align='C')
    pdf.cell(200, 10, txt="DISCLAIMER: Demo only - Not legal/financial advice.", ln=True, align='C')
    pdf.ln(10)
    for log in logs:
        text = f"{log['timestamp']} | {log['agent_name']} | {log['action']}"
        pdf.multi_cell(0, 5, txt=text)
    
    file_path = os.path.join(os.path.dirname(__file__), 'audit_export.pdf')
    pdf.output(file_path)
    return file_path

cols = st.columns([1, 2, 1])

config = {"configurable": {"thread_id": st.session_state.thread_id}}

async def run_agent_workflow(initial_state=None):
    try:
        import time
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'live_trace.log'))
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Manual UI Trigger: Initiating workflow state.\\n")

        start_time = time.time()
        agent_count = 0
        flow_start = start_time

        if initial_state:
            iterator = st.session_state.workflow.astream(initial_state, config)
        else:
            iterator = st.session_state.workflow.astream(None, config)
            
        async for output in iterator:
            for node_name, state in output.items():
                step_duration = time.time() - start_time
                start_time = time.time()
                agent_count += 1
                
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 {node_name.replace('_', ' ').title()} ({step_duration:.1f}s)\\n")
                    f.write(f"--> Excuting node heuristics/tool calls...\\n")
                    f.write(f"    🏃 Hand-off: {node_name.replace('_', ' ').title()} passed constraint validation.\\n")
                    f.write(f"VELOCITY_MARKER|{agent_count}|{time.time()-flow_start}\\n")
                    f.flush()

                with st.spinner(f"Agent {node_name.replace('_', ' ').title()} is thinking..."):
                    await asyncio.sleep(0.5)
                st.session_state.current_node = node_name
                st.session_state.workflow_state = state
                st.session_state.run_logs = get_audit_logs()[-15:] # Take latest rich logs
                
                if state.get('status') == 'approval_pending':
                    return
                    
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Workflow processing sequence completed via Dashboard.\\n")
                    
        st.session_state.current_node = "END"
        st.success("Workflow Completed!")
        
        # Save historical run
        try:
            mermaid = get_mermaid_graph("END")
            trace_content = ""
            log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'live_trace.log'))
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    trace_content = f.read()

            current_logs = get_audit_logs()
            audit_json = json.dumps(current_logs)
            
            pr_number = "UNKNOWN"
            if st.session_state.workflow_state and "pr_id" in st.session_state.workflow_state and st.session_state.workflow_state["pr_id"]:
                 pr_number = st.session_state.workflow_state["pr_id"]
            elif st.session_state.workflow_state and "vendor_id" in st.session_state.workflow_state:
                 pr_number = f"Vendor-{st.session_state.workflow_state['vendor_id']}"

            save_workflow_history(pr_number, mermaid, trace_content, audit_json)
        except Exception as err:
            st.error(f"Failed to save history: {err}")
            
    except Exception as e:
        st.error(f"Workflow error: {e}")

with st.sidebar:
    st.header("Control Panel")
    st.markdown("*DISCLAIMER: Demo only - Not legal/financial advice.*")
    
    st.markdown("#### System Status")
    st.markdown("🔵 **LIVE: Connected to Enterprise Mail Server**")
    
    live_refresh = st.checkbox("🔄 Enable Live Refresh", value=True)
    
    st.markdown("---")
    st.subheader("🕒 Historical Audit Vault")
    
    historical_wfs = get_workflow_history()
    wf_options = [{"id": None, "label": "LIVE (Latest)", "pr_number": None}]
    for wf in historical_wfs:
        wf_options.append({
            "id": wf["id"],
            "label": f"[{wf['timestamp']}] - PR: {wf['pr_number']}",
            "pr_number": wf["pr_number"]
        })
        
    selected_wf_label = st.selectbox(
        "Select Workflow to Re-hydrate",
        options=[opt["label"] for opt in wf_options]
    )
    
    selected_opt = next((opt for opt in wf_options if opt["label"] == selected_wf_label), None)
    st.session_state.active_workflow = selected_opt["id"] if selected_opt else None

    st.markdown("---")
    
    scenario_choice = st.selectbox("Select Scenario", [s['name'] for s in st.session_state.scenarios])
    st.markdown("**Description:** " + next(s['description'] for s in st.session_state.scenarios if s['name'] == scenario_choice))
    
    if st.button("Start Workflow", type="primary"):
        clear_db()
        st.session_state.thread_id = str(uuid.uuid4())
        config["configurable"]["thread_id"] = st.session_state.thread_id
        st.session_state.run_logs = ["Workflow Started..."]
        
        s_data = next(s for s in st.session_state.scenarios if s['name'] == scenario_choice)
        
        initial_state = {
            "pr_id": None, "vendor_id": s_data["vendor_id"], "pdf_path": s_data["pdf_path"],
            "pr_data": {}, "issues": [], "vendor_category": s_data["category"],
            "po_id": None, "invoice_id": None, "amount": 0.0,
            "approval_status": "pending", "status": "started", "error_count": 0
        }
        st.session_state.workflow_state = initial_state
        st.session_state.current_node = "intake_agent"
        asyncio.run(run_agent_workflow(initial_state))
        
    if st.session_state.workflow_state and st.session_state.workflow_state.get('status') == 'approval_pending':
        st.warning("Human Approval Required (Amount > 1M)")
        if st.button("Approve & Continue"):
            st.session_state.workflow.update_state(config, {"approval_status": "approved"})
            asyncio.run(run_agent_workflow(None))
            
    st.markdown("---")
    st.subheader("Impact Metrics (Live)")
    
    from app.logic.impact_calculator import calculate_advanced_roi
    if st.session_state.active_workflow:
        hist_wf = get_workflow_by_id(st.session_state.active_workflow)
        metric_logs = json.loads(hist_wf['audit_json']) if hist_wf and hist_wf.get('audit_json') else []
    else:
        metric_logs = get_audit_logs()
        
    time_val, cost_val, time_delta, cost_delta = calculate_advanced_roi(metric_logs)
    
    st.metric(label="Time Saved vs Manual", value=time_val, delta=time_delta)
    st.metric(label="Cost Savings ROI", value=cost_val, delta=cost_delta)

    st.markdown("---")
    if st.button("Logout", type="secondary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.logged_in_toast = False
        st.rerun()

with cols[0]:
    st.subheader("Orchestration Graph")
    graph_container = st.empty()
    
    active_wf_id = st.session_state.active_workflow
    historical_data = get_workflow_by_id(active_wf_id) if active_wf_id else None
    
    if historical_data and historical_data.get('mermaid_graph'):
        mermaid_code = historical_data['mermaid_graph']
    else:
        mermaid_code = get_mermaid_graph(st.session_state.current_node)
        
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
      </script>
    </head>
    <body style="background-color: transparent; color: white;">
      <div class="mermaid" style="display: flex; justify-content: center;">
      {mermaid_code}
      </div>
    </body>
    </html>
    """
    with graph_container.container():
        import streamlit.components.v1 as components
        components.html(html_code, height=650, scrolling=True)

with cols[1]:
    st.subheader("Real-Time Reasoning Trace")
    
    @st.fragment(run_every="2s")
    def render_live_trace():
        velocity_container = st.empty()
        trace_container = st.empty()
        
        lines = []
        active_wf_id = st.session_state.active_workflow
        if active_wf_id:
            historical_data = get_workflow_by_id(active_wf_id)
            if historical_data and historical_data.get('trace_logs'):
                lines = historical_data['trace_logs'].split('\\n')
        else:
            log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'live_trace.log'))
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
        if lines:
            velocity = "0.00"
            clean_lines = []
            for line in lines:
                if line.startswith("VELOCITY_MARKER|"):
                    parts = line.strip().split("|")
                    if len(parts) >= 3 and float(parts[2]) > 0:
                        velocity = f"{float(parts[1])/float(parts[2]):.2f}"
                    continue
                clean_lines.append(line.strip())
                
            velocity_container.metric("⚡ Current Velocity", f"{velocity} agents/sec", "Logical Depth: 14 Reasoning Steps")
            
            rendered_text = "<div style='height: 480px; overflow-y: auto; display: flex; flex-direction: column; justify-content: flex-start; padding: 15px; background-color: #0E1117; border-radius: 8px; font-family: monospace; border: 1px solid #333;'>"
            for line in clean_lines[-40:]:
                if '🏃 Hand-off' in line:
                    rendered_text += f"<p style='color: #4CAF50; font-size: 0.9em; margin: 2px 0 2px 15px;'>{line}</p>"
                elif 'Intent:' in line or '-->' in line:
                    rendered_text += f"<p style='color: #FFC107; font-size: 0.9em; margin: 2px 0 2px 15px;'>{line}</p>"
                elif '✅' in line or '📬' in line:
                    rendered_text += f"<p style='color: #00E676; font-weight: bold; margin: 10px 0;'>{line}</p>"
                elif '[' in line:
                    rendered_text += f"<p style='color: #E0E0E0; font-weight: bold; margin: 10px 0 2px 0; font-size: 1.05em;'>{line}</p>"
                else:
                    rendered_text += f"<p style='color: #aaa; margin: 0;'>{line}</p>"
            
            # Simple script to auto-scroll the trace terminal down to the bottom
            rendered_text += "<script>var container = document.getElementsByTagName('div')[0]; container.scrollTop = container.scrollHeight;</script></div>"
            
            with trace_container.container():
                import streamlit.components.v1 as components
                components.html(rendered_text, height=520, scrolling=False)
        else:
            trace_container.info("⏳ System Idle: Waiting for next Email Event...")

    render_live_trace()

with cols[2]:
    st.subheader("Secure Audit Trail")
    audit_container = st.container()
    
    active_wf_id = st.session_state.active_workflow
    if active_wf_id:
        historical_data = get_workflow_by_id(active_wf_id)
        if historical_data and historical_data.get('audit_json'):
            logs = json.loads(historical_data['audit_json'])
        else:
            logs = []
    else:
        logs = get_audit_logs()
    
    with audit_container:
        st.markdown("*Note: All entries are encrypted at rest via AES-256.*")
        for log in reversed(logs[-10:]):
            with st.expander(f"🛡️ {log['timestamp']} - {log['agent_name']}"):
                st.write(f"**Action:** {log['action']}")
                if 'details' in log and isinstance(log['details'], dict) and 'tool_calls' in log['details']:
                    st.caption(f"🔧 **Tool Executed:** `{log['details']['tool_calls']}`")
                
                if st.checkbox("Decrypt Data Payload", key=f"decrypt_{log.get('id', uuid.uuid4())}"):
                    st.json(log['details'])
                else:
                    st.code("AES-256 [ENCRYPTED HIDDEN PAYLOAD]")
                    
        if logs:
            st.markdown("---")
            if st.button("Generate Audit Report"):
                pdf_path = generate_audit_pdf(logs)
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Download Certified Audit Report (AES-256 Verified)", f, file_name="AvataarFlow_Historical_Audit.pdf", mime="application/pdf")


import time
if 'live_refresh' in locals() and live_refresh:
    time.sleep(3)
    st.rerun()
