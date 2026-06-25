import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
import hashlib
import os

# Configure page layout
st.set_page_config(
    page_title="Physical Sciences Academic Companion", 
    page_icon="🎓", 
    layout="centered"
)

DB_FILE = "pca_platform.db"

# --- PRODUCTION-GRADE SECURITY: PBKDF2 KEY STRETCHING & SECURE SECRETS ---
# Pull pepper from Streamlit Secrets or environment fallback safely
SECURITY_PEPPER = st.secrets.get("PCA_PEPPER", os.getenv("PCA_PEPPER", "FPS_DEFAULT_LOCAL_PEPPER_2026"))

def secure_hash(password: str, username: str) -> str:
    """Uses PBKDF2 key stretching with 100,000 iterations to enforce slow, brute-force resistant hashing."""
    salt = f"{username.lower()}{SECURITY_PEPPER}".encode('utf-8')
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt, 
        100000 # Enforces computationally heavy execution
    )
    return key.hex()

# --- ENGINE DATABASE & SCHEMA MIGRATION ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Core Account Tables (Enforced Matric Uniqueness)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            matric_no TEXT UNIQUE,
            department TEXT,
            level TEXT,
            date_created TEXT
        )
    """)
    
    # Aggregated Summary Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            department TEXT,
            cgpa REAL,
            units INTEGER,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)
    
    # Course Storage for Audits & Forecasting
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            semester_index INTEGER,
            course_code TEXT,
            units INTEGER,
            grade TEXT,
            points REAL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)
    
    # Schema Migration Gate for older installations
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN matric_no TEXT")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_matric ON users(matric_no)")
    except sqlite3.OperationalError: 
        pass
    try: 
        cursor.execute("ALTER TABLE users ADD COLUMN department TEXT")
    except sqlite3.OperationalError: 
        pass
    try: 
        cursor.execute("ALTER TABLE users ADD COLUMN level TEXT")
    except sqlite3.OperationalError: 
        pass
    try: 
        cursor.execute("ALTER TABLE users ADD COLUMN date_created TEXT")
    except sqlite3.OperationalError: 
        pass
            
    conn.commit()
    conn.close()

init_db()

# Premium Custom CSS
custom_css = """
<style>
    .main { background-color: #fafafa; }
    h1 { color: #4B0082; text-align: center; font-weight: 800; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555; font-size: 14px; margin-bottom: 25px; }
    .result-card {
        background: linear-gradient(135deg, #4B0082 0%, #2A004D 100%);
        color: white; padding: 30px; border-radius: 20px; text-align: center; margin: 20px 0;
    }
    .profile-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 5px solid #4B0082; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .metric-val { font-size: 42px; font-weight: bold; color: #D4AF37; }
    .platform-footer { text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #E0E0E0; }
</style>
"""
# FIXED: Safe positional markdown rendering to stop TypeErrors
st.markdown(custom_css, unsafe_allow_html=True)

if "logged_in_user" not in st.session_state: 
    st.session_state["logged_in_user"] = None
if "user_profile" not in st.session_state: 
    st.session_state["user_profile"] = {}

st.markdown("<h1>🎓 Physical Sciences Academic Companion (PCA)</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Official Portal | Faculty of Physical Sciences</p>", unsafe_allow_html=True)

col_dept, col_auth = st.columns([4, 5])

with col_auth:
    if st.session_state["logged_in_user"] is None:
        auth_action = st.radio("Account Access", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        u_input = st.text_input("Username", max_chars=15, placeholder="Username", key="auth_u").strip()
        p_input = st.text_input("Password", type="password", placeholder="Password", key="auth_p")
        
        if auth_action == "Sign Up":
            reg_matric = st.text_input("Matric Number", placeholder="e.g., FOS/ICH/...", key="reg_mat").strip().upper()
            reg_dept = st.selectbox("Department", ["Computer Science", "Mathematics", "Physics", "Chemistry", "Statistics", "Industrial Chemistry"], key="reg_dep")
            reg_level = st.selectbox("Current Level", ["100L", "200L", "300L", "400L", "500L"], key="reg_lev")
            
            if st.button("Create Secure Account"):
                if u_input and p_input and reg_matric:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT username FROM users WHERE matric_no = ?", (reg_matric,))
                    if cursor.fetchone():
                        st.error("❌ This Matric Number is already tied to an existing account.")
                        conn.close()
                    else:
                        try:
                            hashed_p = secure_hash(p_input, u_input)
                            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cursor.execute("""
                                INSERT INTO users (username, password, matric_no, department, level, date_created) 
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (u_input, hashed_p, reg_matric, reg_dept, reg_level, current_date))
                            conn.commit()
                            
                            st.session_state["logged_in_user"] = u_input
                            st.session_state["user_profile"] = {"matric": reg_matric, "dept": reg_dept, "level": reg_level, "joined": current_date}
                            st.success("Secure profile indexed successfully!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error(f"❌ Username '{u_input}' is already taken.")
                            suggestions = []
                            base_clean = u_input.lower().replace(" ", "")
                            candidate_patterns = [f"{base_clean}{random.randint(10, 99)}", f"{base_clean}_{random.randint(100, 999)}", f"{base_clean}_fps"]
                            for candidate in candidate_patterns:
                                cursor.execute("SELECT username FROM users WHERE username = ?", (candidate,))
                                if not cursor.fetchone(): 
                                    suggestions.append(candidate)
                            st.markdown("**💡 Try an available username variant:**")
                            for sugg in suggestions[:3]: 
                                st.code(sugg)
                        finally:
                            conn.close()
                else:
                    st.warning("All verification elements are mandatory.")
        else:
            if st.button("Secure Sign In"):
                if u_input and p_input:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT password, matric_no, department, level, date_created FROM users WHERE username = ?", (u_input,))
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row and row[0] == secure_hash(p_input, u_input):
                        st.session_state["logged_in_user"] = u_input
                        st.session_state["user_profile"] = {"matric": row[1], "dept": row[2], "level": row[3], "joined": row[4]}
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.warning("Fields cannot be empty.")
    else:
        st.success(f"👤 Account Verified: **{st.session_state['logged_in_user']}**")
        st.caption(f"🛡️ {st.session_state['user_profile']['matric']} | {st.session_state['user_profile']['level']}")
        if st.button("Secure Log Out"):
            st.session_state["logged_in_user"] = None
            st.session_state["user_profile"] = {}
            st.rerun()

with col_dept:
    if st.session_state["logged_in_user"] is not None:
        dept_list = ["Computer Science", "Mathematics", "Physics", "Chemistry", "Statistics", "Industrial Chemistry"]
        default_idx = dept_list.index(st.session_state["user_profile"]["dept"]) if st.session_state["user_profile"]["dept"] in dept_list else 0
        department = st.selectbox("Active Department Context", dept_list, index=default_idx, disabled=True)
    else:
        department = st.selectbox("Select Your Department", ["Computer Science", "Mathematics", "Physics", "Chemistry", "Statistics", "Industrial Chemistry"])

st.markdown("---")

grade_scale = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Multi-Semester Calculator", 
    "🎯 Target Predictor", 
    "🧠 Smart Academic Adviser",
    "📈 Performance Dashboard"
])

# TAB 1: CALCULATION CORE WITH COURSE-LEVEL HISTORY STREAMING
with tab1:
    st.write("Calculate your detailed Semester GPAs and Cumulative CGPA.")
    num_semesters = st.number_input("How many semesters are you calculating for?", min_value=1, max_value=12, value=2, step=1, key="t1_sems")
    
    grand_total_units = 0
    grand_total_points = 0
    calculated_courses_cache = []
    
    for sem in range(int(num_semesters)):
        with st.expander(f"📅 Semester {sem + 1} Details", expanded=(sem == 0)):
            num_courses = st.number_input(f"Number of courses in Semester {sem + 1}", min_value=1, max_value=15, value=5, key=f"t1_nc_{sem}")
            
            sem_units = 0
            sem_points = 0
            
            for i in range(int(num_courses)):
                col1, col2, col3, col4 = st.columns([3, 1.5, 2, 2.5])
                with col1:
                    c_code = st.text_input("Course Code", value=f"CHM{101+i}", key=f"t1_code_{sem}_{i}").upper().strip()
                with col2:
                    c_unit = st.number_input("Units", min_value=1, max_value=6, value=3, key=f"t1_u_{sem}_{i}")
                with col3:
                    input_mode = st.selectbox("Mode", ["Score", "Grade"], key=f"t1_m_{sem}_{i}")
                with col4:
                    if input_mode == "Score":
                        score = st.number_input("Score", min_value=0, max_value=100, value=70, key=f"t1_s_{sem}_{i}")
                        if score >= 70: letter, pt = "A", 5.0
                        elif score >= 60: letter, pt = "B", 4.0
                        elif score >= 50: letter, pt = "C", 3.0
                        elif score >= 45: letter, pt = "D", 2.0
                        elif score >= 40: letter, pt = "E", 1.0
                        else: letter, pt = "F", 0.0
                    else:
                        letter = st.selectbox("Grade", ["A", "B", "C", "D", "E", "F"], key=f"t1_g_{sem}_{i}")
                        pt = grade_scale[letter]
                    st.caption(f"↳ **{letter}** ({int(pt)} Pts)")
                
                sem_units += c_unit
                sem_points += c_unit * pt
                
                calculated_courses_cache.append({
                    "sem_idx": sem + 1, "code": c_code, "units": c_unit, "grade": letter, "pts": pt
                })
                st.markdown("<hr style='margin: 4px 0; border-color: #f0f0f0;'>", unsafe_allow_html=True)
                
            if sem_units > 0:
                st.info(f"**Semester {sem + 1} GPA:** {sem_points / sem_units:.2f}")
                grand_total_units += sem_units
                grand_total_points += sem_points

    if grand_total_units > 0:
        calc_cgpa = grand_total_points / grand_total_units
        st.markdown(f"""<div class="result-card"><p style='letter-spacing: 1px;'>CUMULATIVE CGPA</p><div class="metric-val">{calc_cgpa:.2f}</div><p style='font-size: 13px; opacity: 0.8;'>Total Units: {int(grand_total_units)}</p></div>""", unsafe_allow_html=True)
        
        if st.session_state["logged_in_user"] is not None:
            if st.button("💾 Commit Comprehensive Audit Data to Cloud Log"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("SELECT timestamp FROM history WHERE username = ? ORDER BY id DESC LIMIT 1", (st.session_state["logged_in_user"],))
                last_record = cursor.fetchone()
                if last_record and datetime.now() - datetime.strptime(last_record[0], "%Y-%m-%d %H:%M:%S") < timedelta(minutes=2):
                    st.warning("⚠️ High frequency save intercepted. Wait a moment before logging modifications.")
                else:
                    cursor.execute("INSERT INTO history (username, timestamp, department, cgpa, units) VALUES (?, ?, ?, ?, ?)",
                                   (st.session_state["logged_in_user"], now_str, department, round(calc_cgpa, 2), int(grand_total_units)))
                    
                    for course in calculated_courses_cache:
                        cursor.execute("""
                            INSERT INTO course_history (username, timestamp, semester_index, course_code, units, grade, points)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (st.session_state["logged_in_user"], now_str, course["sem_idx"], course["code"], course["units"], course["grade"], course["pts"]))
                        
                    conn.commit()
                    st.success("🚀 Comprehensive courses and summary records logged permanently.")
                conn.close()

# TAB 2: TARGET TRACKERS
with tab2:
    st.markdown("<h2>🎯 Target Engine</h2>", unsafe_allow_html=True)
    curr_cgpa = st.number_input("Your Current CGPA Baseline", min_value=0.0, max_value=5.0, value=3.42)
    curr_units = st.number_input("Your Earned Credit Units to Date", min_value=1, value=68)
    
    st.markdown("### **Class Standing Target Tracks**")
    fc_progress = min(max(curr_cgpa / 4.50, 0.0), 1.0)
    st.write(f"**First Class Boundary Track (4.50+)** | Progress: {fc_progress*100:.1f}%")
    st.progress(fc_progress)
    
    21_progress = min(max(curr_cgpa / 3.50, 0.0), 1.0)
    st.write(f"**Second Class Upper Track (3.50+)** | Progress: {21_progress*100:.1f}%")
    st.progress(21_progress)

# TAB 3: SMART DATA-DRIVEN ACADEMIC ADVISER
with tab3:
    st.markdown("<h2>🧠 Data-Driven Diagnostics</h2>", unsafe_allow_html=True)
    user_status_gpa = st.number_input("Verify standing profile GPA context for advice details:", min_value=0.0, max_value=5.0, value=3.47)
    
    st.markdown("#### **Actionable Vector Diagnostics:**")
    if user_status_gpa < 3.50 and user_status_gpa >= 3.40:
        diff = 3.50 - user_status_gpa
        st.warning(f"💡 **Target Delta Warning:** You are exactly **{diff:.2f} points** away from a **Second Class Upper (2:1)** standing.")
        st.markdown("- Securing an **A** grade inside an upcoming 3-unit fundamental course injects exactly **15 Quality Points** into your tracking ledger, dropping your gap requirement significantly.")
    elif user_status_gpa >= 4.50:
        st.success("🏆 **Elite Multiplier Standing:** Your position is secure. Prioritize heavy credit load courses (3-unit and 4-unit sequences) to defend this high margin vector.")
    else:
        st.info("📊 **Stability Path Optimization:** Focus heavily on clearing minor foundational deficiencies. Transforming low mark entries into predictable 'B' profiles offers high return vectors.")

# TAB 4: ADVANCED GRAPHICAL DASHBOARD
with tab4:
    st.markdown("<h2>📈 Performance Analytics Vault</h2>", unsafe_allow_html=True)
    if st.session_state["logged_in_user"] is None:
        st.info("Log in with your institutional credentials to draw historical dashboards.")
    else:
        profile = st.session_state["user_profile"]
        
        st.markdown(f"""<div class="profile-card"><h3 style="margin:0 0 10px 0; color:#4B0082;">STUDENT CARD: {st.session_state['logged_in_user'].upper()}</h3><p style="margin:2px 0;"><b>Matriculation ID:</b> {profile['matric']}</p><p style="margin:2px 0;"><b>Department:</b> {profile['dept']}</p><p style="margin:2px 0;"><b>Level Tracking:</b> {profile['level']}</p></div>""", unsafe_allow_html=True)
        
        conn = sqlite3.connect(DB_FILE)
        df_summary = pd.read_sql_query("SELECT timestamp, department, cgpa, units FROM history WHERE username = ? ORDER BY id ASC", conn, params=(st.session_state["logged_in_user"],))
        df_courses = pd.read_sql_query("SELECT semester_index as 'Semester', course_code as 'Course', units as 'Units', grade as 'Grade', points as 'Points' FROM course_history WHERE username = ? ORDER BY id ASC", conn, params=(st.session_state["logged_in_user"],))
        conn.close()
        
        if df_summary.empty:
            st.write("No saved telemetry records indexed yet. Save an evaluation row inside Tab 1.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Database Submissions", len(df_summary))
            with col2: st.metric("Peak CGPA Recorded", f"{df_summary['cgpa'].max():.2f}")
            with col3: st.metric("Current Entry Mark", f"{df_summary['cgpa'].iloc[-1]:.2f}")
            
            st.subheader("📉 Historical CGPA Progression Chart")
            st.line_chart(df_summary["cgpa"])
            
            if not df_courses.empty:
                st.subheader("📋 Detailed Course Audit Records")
                st.dataframe(df_courses, use_container_width=True, hide_index=True)

st.markdown("""<div class="platform-footer"><p style='font-weight: bold; color: #4B0082; margin-bottom: 2px;'>Physical Sciences Academic Companion (PCA)</p><p style='font-size: 12px; color: #777; margin-top: 0;'>Secure Production Engine Build v4.0</p></div>""", unsafe_allow_html=True)
