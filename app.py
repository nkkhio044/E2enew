import streamlit as st
import json
import os
import hashlib
import platform
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# --- CONFIG & DATABASE (Wahi purana) ---
USER_PASSWORD = "ArYan.x3" 
ADMIN_PASSWORD = "MASTER_ADMIN_99" 
DB_FILE = "approvals.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def get_permanent_key(name):
    device_id = platform.node() + platform.machine()
    return "KEY_" + hashlib.sha256(f"{name}_{device_id}".encode()).hexdigest()[:12].upper()

# --- UI SETUP ---
st.set_page_config(page_title="ArYan.x3 E2E", layout="centered")

if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# Admin Section
with st.sidebar:
    st.header("🛡️ Admin Panel")
    a_pwd = st.text_input("Admin Pass", type="password")
    if st.button("Admin Login"):
        if a_pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.rerun()

if st.session_state.is_admin:
    db = load_db()
    u_n = st.text_input("Name")
    u_k = st.text_input("Key")
    if st.button("Approve"):
        db[u_k] = u_n
        save_db(db)
        st.success("Approved!")
    st.write(db)
    if st.button("Logout Admin"):
        st.session_state.is_admin = False
        st.rerun()

st.divider()
if not st.session_state.logged_in:
    u_p = st.text_input("Tool Password", type="password")
    if st.button("Unlock"):
        if u_p == USER_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
else:
    u_name = st.text_input("Enter Your Name")
    if u_name:
        my_key = get_permanent_key(u_name)
        st.info(f"Your Key: {my_key}")
        db = load_db()
        if my_key in db:
            st.success(f"Welcome {u_name}")
            cookies = st.text_area("Cookies")
            target = st.text_input("Target UID")
            hater = st.text_input("Hater Name")
            speed = st.number_input("Speed", min_value=1, value=10)
            file = st.file_uploader("Upload .txt")

            if st.button("🚀 START SENDING"):
                msgs = file.getvalue().decode().splitlines()
                
                options = Options()
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.binary_location = "/usr/bin/chromium"
                
                try:
                    driver = webdriver.Chrome(options=options)
                    
                    # --- LOGIN LOGIC ---
                    driver.get("https://m.facebook.com")
                    for c in cookies.split(';'):
                        if '=' in c:
                            n, v = c.strip().split('=', 1)
                            driver.add_cookie({'name': n.strip(), 'value': v.strip(), 'domain': '.facebook.com'})
                    driver.refresh()
                    time.sleep(5)

                    # --- NAVIGATION ---
                    driver.get(f"https://www.facebook.com/messages/e2ee/t/{target}")
                    st.warning("E2E Loading... 20s")
                    time.sleep(20)

                    # --- SAME SENDING LOGIC AS YOUR SCRIPT ---
                    status_log = st.empty()
                    count = 0
                    while True:
                        for m in msgs:
                            if not m.strip(): continue
                            full_m = f"{hater} {m}" if hater else m
                            
                            # Aapki script wala direct element finding logic
                            # E2EE mein textbox 'role' use karta hai
                            msg_box = driver.find_element(By.XPATH, "//div[@role='textbox']")
                            msg_box.send_keys(full_m)
                            time.sleep(1)
                            msg_box.send_keys(Keys.ENTER)
                            
                            count += 1
                            status_log.success(f"✅ Sent #{count}: {m}")
                            time.sleep(speed)
                            
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    if 'driver' in locals(): driver.quit()
        else:
            st.error("Approval Pending!")
