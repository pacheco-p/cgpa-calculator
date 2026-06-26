import streamlit as st
from database import init_db
import auth
import helpers
import analytics

st.set_page_config(page_title="PCA Portal", page_icon="🎓", layout="centered")
init_db()

# Premium CSS Layer
st.markdown("""
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
    .metric-val { font-size: 42px; font-weight: bold; color: #D4AF37; margin: 10px 0;}
    .platform-footer { text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #E0E0E0; }
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state: st.session_state["user"] = None

st.markdown("<h1>🎓 Physical Sciences Academic Companion (PCA)</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Official Portal | Faculty of Physical Sciences</p>", unsafe_allow_html=True)

col_dept, col_auth = st.columns([4, 5])

with col_auth:
    if st.session_state["user"] is None:
        auth_action = st.radio("Access", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        u = st.text_input("Username", max_chars=15, placeholder="Username").strip()
        p = st.text_input("Password", type="password", placeholder="Password")
        
        if auth_action == "Sign Up":
            mat = st.text_input("Matric Number", placeholder="FOS/ICH/...").strip()
            dept = st.selectbox("Department", ["Computer Science", "Mathematics", "Physics", "Chemistry", "Statistics", "Industrial Chemistry"])
            lvl = st.selectbox("Level", ["100L", "200L", "300L", "400L", "500L"])
            if st.button("Create Profile"):
                if u and p and mat:
                    success, msg = auth.register_user(u, p, mat, dept, lvl)
                    if success:
                        st.success("Account initialized! Please flip to Login mode.")
                    else: st.error(msg)
                else: st.warning("Please fill out all input parameters.")
        else:
            if st.button("Secure Login"):
                success, res = auth.authenticate_user(u, p)
                if success:
                    st.session_state["user"] = res
                    st.rerun()
                else: st.error(res)
    else:
        st.success(f"👤 Session Verified: {st.session_state['user']['username'].upper()}")
        if st.button("Sign Out"):
            st.session_state["user"] = None
            st.rerun()

with col_dept:
    active_dept = st.selectbox(
        "Active Faculty Context", 
        ["Computer Science", "Mathematics", "Physics", "Chemistry", "Statistics", "Industrial Chemistry"],
        disabled=(st.session_state["user"] is not None),
        index=["Computer Science", "Mathematics", "Physics", "Chemistry", "Statistics", "Industrial Chemistry"].index(st.session_state["user"]["dept"]) if st.session_state["user"] else 0
    )

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📊 Multi-Semester Calculator", "🎯 Target Engine", "📈 Performance Analytics"])

# TAB 1: CORE CALCULATOR
with tab1:
    # Academic Label Map for easy human-readable headers
    semester_labels = [
        "100L - 1st Semester", "100L - 2nd Semester",
        "200L - 1st Semester", "200L - 2nd Semester",
        "300L - 1st Semester", "300L - 2nd Semester",
        "400L - 1st Semester", "400L - 2nd Semester",
        "500L - 1st Semester", "500L - 2nd Semester",
        "600L - 1st Semester", "600L - 2nd Semester"
    ]
    
    num_sems = st.number_input("Number of Semesters to Calculate", min_value=1, max_value=12, value=1)
    g_units, g_pts, courses_cache = 0, 0, []
    
    for sem in range(int(num_sems)):
        sem_label = semester_labels[sem] if sem < len(semester_labels) else f"Semester {sem + 1}"
        
        with st.expander(f"📅 {sem_label}", expanded=(sem == 0)):
            num_courses = st.number_input(f"Number of Courses", min_value=1, max_value=12, value=4, key=f"nc_{sem}")
            for i in range(int(num_courses)):
                c1, c2, c3 = st.columns([4, 2, 3])
                with c1: 
                    # Left completely blank for the user to type manually without forced defaults
                    code = st.text_input("Course Code", placeholder="e.g., CHM101", key=f"c_{sem}_{i}").upper().strip()
                with c2: 
                    units = st.number_input("Units", min_value=1, max_value=6, value=3, key=f"u_{sem}_{i}")
                with c3: 
                    grade = st.selectbox("Grade", ["A", "B", "C", "D", "E", "F"], key=f"g_{sem}_{i}")
                
                pts = {"A":5,"B":4,"C":3,"D":2,"E":1,"F":0}[grade]
                g_units += units
                g_pts += (units * pts)
                courses_cache.append({"sem_idx": sem+1, "code": code, "units": units, "grade": grade, "pts": pts})
                
    if g_units > 0:
        calc_cgpa = g_pts / g_units
        st.markdown(f"""
            <div class="result-card">
                <p style='letter-spacing: 1px; margin:0;'>AGGREGATE CUMULATIVE CGPA</p>
                <div class="metric-val">{calc_cgpa:.2f}</div>
                <div style='margin-bottom:15px;'>{helpers.get_class_badge(calc_cgpa)}</div>
                <p style='font-size: 13px; opacity: 0.8; margin:0;'>Total Quality Checked Units: {g_units}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state["user"] is not None:
            if st.button("💾 Commit Evaluation To Cloud Registry"):
                analytics.save_audit_session(st.session_state["user"]["username"], active_dept, calc_cgpa, g_units, courses_cache)
                st.success("Session saved successfully!")

# TAB 2: TARGET TRUCKS
with tab2:
    st.markdown("### Class Target Analytics")
    curr_cgpa = st.number_input("Baseline CGPA", min_value=0.0, max_value=5.0, value=3.0)
    st.write(f"First Class Progress Profile (4.50+): {min(max(curr_cgpa/4.5,0.0),1.0)*100:.1f}%")
    st.progress(min(max(curr_cgpa/4.5,0.0),1.0))

# TAB 3: ANALYTICS VAULT
with tab3:
    if st.session_state["user"] is not None:
        analytics.render_dashboard(st.session_state["user"]["username"])
    else:
        st.info("Log in to pull historical analytics data logs.")

# Professional Team Attribution Footer
st.markdown("""
<div class="platform-footer">
    <p style='font-weight: bold; color: #4B0082; margin-bottom: 2px;'>Physical Sciences Academic Companion (PCA)</p>
    <p style='font-size: 13px; color: #555; margin-bottom: 2px;'>Developed by <b>Pedro</b> & Team</p>
    <p style='font-size: 11px; color: #888; margin-top: 0;'>Secure Production Engine Build v5.0</p>
</div>
""", unsafe_allow_html=True)
