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
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

# === CONFIGURATION ===
USER_PASSWORD = "ArYan.x3" 
ADMIN_PASSWORD = "MASTER_ADMIN_99" 
DB_FILE = "approvals.json"
BANNER_URL = "https://i.ibb.co/vz6mP0X/your-banner.jpg"

# === DATABASE LOGIC ===
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def get_permanent_key(name):
    device_id = platform.node() + platform.machine()
    return "KEY_" + hashlib.sha256(f"{name}_{device_id}".encode()).hexdigest()[:12].upper()

# === UI INTERFACE ===
st.set_page_config(page_title="ArYan.x3 E2E", layout="centered")
st.image(BANNER_URL)

if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.header("🛡️ Admin Panel")
    a_pwd = st.text_input("Admin Pass", type="password")
    if st.button("Admin Login"):
        if a_pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.rerun()

if st.session_state.is_admin:
    st.header("🔑 Approval Manager")
    db = load_db()
    u_name_app = st.text_input("Name to Approve")
    u_key_app = st.text_input("Key to Approve")
    if st.button("✅ Approve"):
        if u_name_app and u_key_app:
            db[u_key_app] = u_name_app
            save_db(db)
            st.success("User Approved!")
            st.rerun()
    st.write("Approved Users:", db)
    if st.button("Logout Admin"):
        st.session_state.is_admin = False
        st.rerun()

# --- USER SECTION ---
st.divider()
if not st.session_state.logged_in:
    pwd_input = st.text_input("Enter Tool Password", type="password")
    if st.button("Unlock"):
        if pwd_input == USER_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong Password!")
else:
    user_name = st.text_input("Enter Your Name")
    if user_name:
        p_key = get_permanent_key(user_name)
        st.info(f"Your Key: {p_key}")
        
        db = load_db()
        if p_key in db:
            st.success(f"✅ Welcome {user_name}!")
            
            # Inputs
            cookies = st.text_area("Paste Cookies")
            target_uid = st.text_input("Target UID")
            hater = st.text_input("Hater Name")
            speed = st.number_input("Speed (Seconds)", min_value=1, value=10)
            file = st.file_uploader("Upload Message File (.txt)")

            if st.button("🚀 START SENDING"):
                if cookies and target_uid and file:
                    msgs = file.getvalue().decode("utf-8").splitlines()
                    
                    options = Options()
                    options.add_argument("--headless=new")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-gpu")
                    
                    # === NETWORK & DNS FIXES ===
                    options.add_argument("--disable-ipv6")
                    options.add_argument("--dns-prefetch-disable")
                    options.add_argument("--ignore-certificate-errors")
                    options.add_argument("--proxy-server='direct://'")
                    options.add_argument("--proxy-bypass-list=*")
                    options.binary_location = "/usr/bin/chromium"
                    
                    try:
                        service = Service("/usr/bin/chromedriver")
                        driver = webdriver.Chrome(service=service, options=options)
                        driver.set_page_load_timeout(60)
                        
                        # --- STEP 1: LOGIN ---
                        st.info("🔄 Checking Login Connection...")
                        # DNS fail se bachne ke liye direct retry logic
                        try:
                            driver.get("https://m.facebook.com")
                        except:
                            driver.get("https://m.facebook.com") # Second attempt
                        
                        time.sleep(3)
                        
                        for c in cookies.split(';'):
                            if '=' in c:
                                n, v = c.strip().split('=', 1)
                                driver.add_cookie({'name': n.strip(), 'value': v.strip(), 'domain': '.facebook.com'})
                        
                        driver.refresh()
                        time.sleep(5)
                        
                        if "login" in driver.current_url or "checkpoint" in driver.current_url:
                            st.error("❌ Login Failed! Cookies Expired.")
                            driver.quit()
                            st.stop()
                        else:
                            st.success("✅ Login Successful!")

                        # --- STEP 2: E2E CHAT ---
                        clean_id = target_uid.split('/')[-1]
                        driver.get(f"https://www.facebook.com/messages/e2ee/t/{clean_id}")
                        st.warning("⏳ Loading Encrypted Chat... 20s Wait")
                        time.sleep(20)

                        # --- STEP 3: SENDING ---
                        status = st.empty()
                        count = 0
                        while True:
                            for m in msgs:
                                if not m.strip(): continue
                                final_m = f"{hater} {m}" if hater else m
                                
                                actions = ActionChains(driver)
                                actions.send_keys(final_m).send_keys(Keys.ENTER).perform()
                                
                                count += 1
                                status.success(f"📩 Sent #{count}: {m}")
                                time.sleep(speed)
                    
                    except Exception as e:
                        st.error(f"⚠️ Network/Connection Error: {e}")
                    finally:
                        if 'driver' in locals(): driver.quit()
        else:
            st.error("❌ Approval Pending! Send key to Admin.")