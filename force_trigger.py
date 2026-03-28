import sys
import os
import asyncio
import shutil
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.watcher_service import run_avataar_flow

src = os.path.join("tests", "data", "scenario_2_pr.pdf")
dst = os.path.join("data", "mail_inbox", "Messy_PR_Scenario.pdf")
os.makedirs(os.path.dirname(dst), exist_ok=True)

shutil.copy(src, dst)

print("Forcing live AvataarFlow trigger to sync dashboard...")
success = asyncio.run(run_avataar_flow(os.path.abspath(dst), "sreedharshini777@gmail.com"))

if success:
    history = os.path.join("data", "processed_history")
    os.makedirs(history, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "sreedharshini777[at]gmail.com"
    moved = os.path.join(history, f"{stamp}_{safe}_Messy_PR_Scenario.pdf")
    shutil.move(dst, moved)
    print("Force-trigger complete. The Live Refresh on Streamlit will now pick this up!")
