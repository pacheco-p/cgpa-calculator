import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configure page layout
st.set_page_config(
    page_title="Physical Sciences Academic Companion", 
    page_icon="🎓", 
    layout="centered"
)

# --- DATABASE SETUP ENGINE (SQLite Persistence) ---
DB_FILE = "pca_platform.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
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
    conn.commit()
    conn.close()

init_db()

# Premium Neutral Styling with Markdown protection fixes
custom_css = """
<style>
    .main { background-color: #fafafa; }
    h1 { color: #4B0082; text-align: center; font-weight: 800; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #555; font-size: 14px; margin-bottom: 25px; }
    .zone-badge {
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
        text-align: center;
    }
    .first-class { background-color: #D4AF37; color: #4B0082; }
    .upper-division { background-color: #4B0082; color: white; }
    .lower-division { background-color: #E6E6FA; color: #4B0082; border: 1px solid #4B0082; }
    .third-class { background-color: #FFE4B5; color: #8B4513; }
    .pass-zone { background-color: #E0E0E0; color: #333; }
    .danger-zone { background-color: #FFC0CB; color: #D8000C; }
    
    .result-card {
        background: linear-gradient(135deg, #4B0082 0%, #2A004D 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(75,0,130,0.15);
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .metric-val { font-size: 42px; font-weight: bold; color: #D4AF37; }
    .platform-footer {
        text-align: center;
        margin-top: 60px;
        padding-top: 20px;
        border-top: 1px solid #E0E0E0;
    }
</style>
"""
st.markdown(body=custom_css, unsafe_allow_html=True)

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# App Headers
st.markdown(body="<h1>🎓 Physical Sciences Academic Companion (PCA)</h1>", unsafe_allow_html=True)
st.markdown(body="<p class='subtitle'>Built by Students, For Students</p>", unsafe_allow_html=True)

# Auth Panel & Department Selector
col_dept, col_auth = st.columns([1, 1])

with col_dept:
    department = st.selectbox(
        "Select Your Department",
        ["Computer Science", "Mathematics", "Physics", "Chemistry", "Statistics", "Industrial Chemistry"]
    )

with col_auth:
    if st.session_state["logged_in_user"] is None:
        auth_action = st.radio("Account Access", ["Login", "Sign Up"], horizontal=True)
        u_input = st.text_input("Username", max_chars=15, placeholder="Username", key="auth_u").strip()
        p_input = st.text_input("Password", type="password", placeholder="Password", key="auth_p")
        
        if auth_action == "Sign Up":
            if st.button("Create Secure Account"):
                if u_input and p_input:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u_input, p_input))
                        conn.commit()
                        st.session_state["logged_in_user"] = u_input
                        st.success("Account created successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already registered.")
                    finally:
                        conn.close()
                else:
                    st.warning("Please fill out all fields.")
        else:
            if st.button("Secure Sign In"):
                if u_input and p_input:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT password FROM users WHERE username = ?", (u_input,))
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row and row[0] == p_input:
                        st.session_state["logged_in_user"] = u_input
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.warning("Fields cannot be empty.")
    else:
        st.write(f"👤 Account Active: **{st.session_state['logged_in_user']}**")
        if st.button("Secure Log Out"):
            st.session_state["logged_in_user"] = None
            st.rerun()

st.markdown("---")

grade_scale = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}

def get_zone_badge(cgpa):
    if cgpa >= 4.50: return '<div class="zone-badge first-class">🏆 First Class</div>'
    elif cgpa >= 3.50: return '<div class="zone-badge upper-division">🔥 Second Class Upper (2:1)</div>'
    elif cgpa >= 2.40: return '<div class="zone-badge lower-division">📈 Second Class Lower (2:2)</div>'
    elif cgpa >= 1.50: return '<div class="zone-badge third-class">📊 Third Class</div>'
    elif cgpa >= 1.00: return '<div class="zone-badge pass-zone">🎯 Pass</div>'
    else: return '<div class="zone-badge danger-zone">⚠️ Fail / Probation</div>'

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Multi-Semester Calculator", 
    "🎯 Target & 'What-If' Predictor", 
    "🧠 Smart Academic Adviser",
    "📈 Saved Analytics & Dashboard"
])

# TAB 1: CALCULATION ENGINE
with tab1:
    st.write("Calculate your detailed Semester GPAs and Cumulative CGPA using scores or grades.")
    num_semesters = st.number_input("How many semesters are you calculating for?", min_value=1, max_value=12, value=2, step=1, key="t1_sems")
    
    grand_total_units = 0
    grand_total_points = 0
    
    for sem in range(int(num_semesters)):
        with st.expander(f"📅 Semester {sem + 1} Details", expanded=(sem == 0)):
            num_courses = st.number_input(f"Number of courses in Semester {sem + 1}", min_value=1, max_value=15, value=5, key=f"t1_nc_{sem}")
            
            sem_units = 0
            sem_points = 0
            
            for i in range(int(num_courses)):
                st.markdown(f"**Course #{i+1}**")
                col1, col2, col3, col4 = st.columns([2, 1, 1.5, 2])
                
                with col1:
                    course_code = st.text_input("Course Code", value=f"COURSE {i+1}", key=f"t1_code_{sem}_{i}").upper()
                with col2:
                    course_unit = st.number_input("Units", min_value=1, max_value=6, value=3, key=f"t1_u_{sem}_{i}")
                with col3:
                    input_mode = st.selectbox("Input By", ["Score (0-100)", "Direct Grade"], key=f"t1_m_{sem}_{i}")
                with col4:
                    if input_mode == "Score (0-100)":
                        score = st.number_input("Score", min_value=0, max_value=100, value=70, key=f"t1_s_{sem}_{i}")
                        if score >= 70: letter, pt = "A", 5.0
                        elif score >= 60: letter, pt = "B", 4.0
                        elif score >= 50: letter, pt = "C", 3.0
                        elif score >= 45: letter, pt = "D", 2.0
                        elif score >= 40: letter, pt = "E", 1.0
                        else: letter, pt = "F", 0.0
                        st.markdown(body=f"<p style='color: #4B0082; font-size: 11px; margin-top: -5px;'>↳ Grade: <b>{letter}</b> ({int(pt)} Pts)</p>", unsafe_allow_html=True)
                    else:
                        letter = st.selectbox("Choose Grade", ["A", "B", "C", "D", "E", "F"], key=f"t1_g_{sem}_{i}")
                        pt = grade_scale[letter]
                        st.markdown(body=f"<p style='color: #4B0082; font-size: 11px; margin-top: -5px;'>↳ Points: <b>{int(pt)} Pts</b></p>", unsafe_allow_html=True)
                
                sem_units += course_unit
                sem_points += course_unit * pt
                st.markdown(body="<hr style='margin: 8px 0; border-color: #eee;'>", unsafe_allow_html=True)
                
            if sem_units > 0:
                sem_gpa = sem_points / sem_units
                st.info(f"**Semester {sem + 1} GPA:** {sem_gpa:.2f} | **Total Units:** {int(sem_units)}")
                grand_total_units += sem_units
                grand_total_points += sem_points

    if grand_total_units > 0:
        calc_cgpa = grand_total_points / grand_total_units
        st.markdown("---")
        st.subheader("📷 Academic Standing Summary")
        
        st.markdown(body=f"""
            <div class="result-card">
                <h2 style='color: #D4AF37; margin-bottom: 2px;'>PHYSICAL SCIENCES ACADEMIC COMPANION</h2>
                <p style='margin-top: 0; font-size: 13px; opacity: 0.8;'>DEPARTMENT OF {department.upper()}</p>
                <hr style='border-color: rgba(255,255,255,0.15);'>
                <p style='font-size: 16px; margin-bottom: 0; letter-spacing: 1px;'>OFFICIAL STANDING</p>
                <div class="metric-val">{calc_cgpa:.2f} / 5.00</div>
                {get_zone_badge(calc_cgpa)}
                <p style='font-size: 13px; opacity: 0.8; margin-top: 15px;'>Total Evaluated Credit Units: <b>{int(grand_total_units)}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        degree_txt = "First Class" if calc_cgpa >= 4.5 else ("Second Class Upper" if calc_cgpa >= 3.5 else ("Second Class Lower" if calc_cgpa >= 2.4 else "Third Class/Pass"))
        report_data = (
            f"=== PCA ACADEMIC STANDING REPORT ===\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Department: {department}\n"
            f"Total Units: {int(grand_total_units)}\n"
            f"Calculated CGPA: {calc_cgpa:.2f} / 5.00\n"
            f"Classification: {degree_txt}\n"
            f"Generated via Physical Sciences Academic Companion (PCA)\n"
        )
        
        st.download_button(
            label="📥 Download Official Result Report",
            data=report_data,
            file_name="PCA_Academic_Result.txt",
            mime="text/plain"
        )
        
        if st.session_
