import streamlit as st
import json
import os
import hashlib
import platform
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# === CONFIG ===
USER_PASSWORD = "ArYan.x3"
ADMIN_PASSWORD = "MASTER_ADMIN_99"
DB_FILE = "approvals.json"
BANNER_URL = "https://i.ibb.co/vz6mP0X/your-banner.jpg"

if "active_tasks" not in st.session_state:
    st.session_state.active_tasks = {}

# === MOBILE-FIRST CSS ===
st.markdown(f"""
<style>
    /* Animated Gradient Background */
    .stApp {{
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #000000);
        background-size: 400% 400%;
        animation: gradient 10s ease infinite;
    }}
    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Mobile Responsive Inputs */
    input, textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 16px !important; /* Mobile par zoom hone se rokta hai */
        border-radius: 8px !important;
    }}

    /* Task Box Styling */
    .task-card {{
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 5px solid #00ffcc;
    }}

    /* Banner Image Optimization */
    .banner-img {{
        width: 100%;
        height: auto;
        border-radius: 10px;
        margin-bottom: 20px;
    }}

    /* Footer Aryan Style */
    .footer {{
        text-align: center;
        padding: 20px;
        color: #00ffcc;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 2px;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 50px;
    }}
</style>
""", unsafe_allow_html=True)

# === LOGIC FUNCTIONS ===
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def get_p_key(name):
    dev_id = platform.node() + platform.machine()
    return "KEY_" + hashlib.sha256(f"{name}_{dev_id}".encode()).hexdigest()[:12].upper()

# Background Runner Logic (Same as before but with safety)
def run_task(u_key, t_id, cookies, target, hater, msgs, speed):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.binary_location = "/usr/bin/chromium"
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://m.facebook.com")
        for c in cookies.split(';'):
            if '=' in c:
                n, v = c.strip().split('=', 1)
                driver.add_cookie({'name': n.strip(), 'value': v.strip(), 'domain': '.facebook.com'})
        driver.refresh()
        time.sleep(5)
        driver.get(f"https://www.facebook.com/messages/e2ee/t/{target}")
        time.sleep(20)

        while st.session_state.active_tasks.get(u_key, {}).get(t_id, {}).get("run"):
            for m in msgs:
                if not st.session_state.active_tasks.get(u_key, {}).get(t_id, {}).get("run"): break
                full_m = f"{hater} {m}" if hater else m
                try:
                    box = driver.find_element(By.XPATH, "//div[@role='textbox']")
                    box.send_keys(full_m + Keys.ENTER)
                    st.session_state.active_tasks[u_key][t_id]["count"] += 1
                except: pass
                time.sleep(speed)
    except: pass
    finally:
        if 'driver' in locals(): driver.quit()

# === UI CONTENT ===
st.markdown(f'<img src="{BANNER_URL}" class="banner-img">', unsafe_allow_html=True)

# (Admin Logic remains same for Approval)
# ...

user_name = st.text_input("Enter Your Name", placeholder="Bittu...")
if user_name:
    my_key = get_p_key(user_name)
    db = load_db()
    if my_key in db:
        st.info(f"🔑 Key: {my_key}")
        
        # UI Columns for Mobile
        tab1, tab2 = st.tabs(["🚀 Create Task", "🛑 Stop Tasks"])
        
        with tab1:
            c_data = st.text_area("Paste Cookies", height=100)
            t_id = st.text_input("Target ID")
            h_name = st.text_input("Hater Name")
            spd = st.number_input("Speed", 5, 300, 10)
            f = st.file_uploader("Upload Message File")
            
            if st.button("START TASK"):
                tid = str(int(time.time()))
                if my_key not in st.session_state.active_tasks: st.session_state.active_tasks[my_key] = {}
                msgs = f.getvalue().decode().splitlines()
                st.session_state.active_tasks[my_key][tid] = {
                    "run": True, "count": 0, "target": t_id, "start": datetime.now().strftime("%I:%M %p (%d %b)")
                }
                threading.Thread(target=run_task, args=(my_key, tid, c_data, t_id, h_name, msgs, spd)).start()
                st.success("Task Started!")

        with tab2:
            tasks = st.session_state.active_tasks.get(my_key, {})
            if not any(t["run"] for t in tasks.values()):
                st.write("No active tasks.")
            for tid, tinfo in list(tasks.items()):
                if tinfo["run"]:
                    st.markdown(f"""
                    <div class="task-card">
                        <b>🎯 Target:</b> {tinfo['target']}<br>
                        <b>🕒 Started:</b> {tinfo['start']}<br>
                        <b>📩 Sent:</b> {tinfo['count']}
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"STOP TASK {tid[-4:]}", key=tid):
                        st.session_state.active_tasks[my_key][tid]["run"] = False
                        st.rerun()

# === FOOTER ===
st.markdown("""
    <div class="footer">
        --- MADE BY ARYAN WEB DEVELOPER --- <br>
        ♛ THE KING OF E2E AUTOMATION ♛
    </div>
""", unsafe_allow_html=True)
