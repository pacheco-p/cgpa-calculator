import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="Physical Sciences Academic Companion", 
    page_icon="🎓", 
    layout="centered"
)

# Premium Neutral Purple & Slate Theme Styling
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
st.markdown(custom_css, unsafe_allow_html=True)

# --- USER ACCOUNTS DATABASE SYSTEM (SESSION STATE BASED) ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {}
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "user_history" not in st.session_state:
    st.session_state["user_history"] = {}

# Main Title Headers
st.markdown("<h1>🎓 Physical Sciences Academic Companion (PCA)</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Built by Students, For Students</p>", unsafe_allow_html=True)

# Top Bar: Department Picker & Authentication Engine
col_dept, col_auth = st.columns([5, 4])

with col_dept:
    department = st.selectbox(
        "Select Your Department",
        [
            "Computer Science",
            "Mathematics",
            "Physics",
            "Chemistry",
            "Statistics",
            "Industrial Chemistry"
        ]
    )

with col_auth:
    if st.session_state["current_user"] is None:
        auth_action = st.radio("Account Access", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        user_input = st.text_input("Username", max_chars=15, key="username_field", placeholder="Enter username")
        
        if auth_action == "Sign Up":
            if st.button("Create Account"):
                if user_input.strip() and user_input not in st.session_state["user_db"]:
                    st.session_state["user_db"][user_input] = user_input
                    st.session_state["user_history"][user_input] = []
                    st.session_state["current_user"] = user_input
                    st.rerun()
                elif user_input in st.session_state["user_db"]:
                    st.error("User exists!")
        else:
            if st.button("Sign In"):
                if user_input in st.session_state["user_db"]:
                    st.session_state["current_user"] = user_input
                    st.rerun()
                else:
                    st.error("Not found.")
    else:
        st.success(f"👤 Active Profile: **{st.session_state['current_user']}**")
        if st.button("Log Out"):
            st.session_state["current_user"] = None
            st.rerun()

st.markdown("---")

# Grade Translation Matrix
grade_scale = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}

def get_zone_badge(cgpa):
    if cgpa >= 4.50: return '<div class="zone-badge first-class">🏆 First Class</div>'
    elif cgpa >= 3.50: return '<div class="zone-badge upper-division">🔥 Second Class Upper (2:1)</div>'
    elif cgpa >= 2.40: return '<div class="zone-badge lower-division">📈 Second Class Lower (2:2)</div>'
    elif cgpa >= 1.50: return '<div class="zone-badge third-class">📊 Third Class</div>'
    elif cgpa >= 1.00: return '<div class="zone-badge pass-zone">🎯 Pass</div>'
    else: return '<div class="zone-badge danger-zone">⚠️ Fail / Probation</div>'

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Multi-Semester Calculator", 
    "🎯 Target & 'What-If' Predictor", 
    "🧠 Smart Academic Adviser",
    "💾 Saved History"
])

# TAB 1: CALC ENGINE
with tab1:
    st.write("Calculate your detailed Semester GPAs and Cumulative CGPA using scores or grades.")
    num_semesters = st.number_input("How many semesters are you calculating for?", min_value=1, max_value=12, value=2, step=1, key="tab1_sems")
    
    grand_total_units = 0
    grand_total_points = 0
    
    for sem in range(int(num_semesters)):
        with st.expander(f"📅 Semester {sem + 1} Details", expanded=(sem == 0)):
            num_courses = st.number_input(f"Number of courses in Semester {sem + 1}", min_value=1, max_value=15, value=5, key=f"t1_num_c_{sem}")
            
            sem_units = 0
            sem_points = 0
            
            for i in range(int(num_courses)):
                st.markdown(f"**Course #{i+1}**")
                col1, col2, col3, col4 = st.columns([3, 1.5, 2, 2.5])
                
                with col1:
                    course_code = st.text_input("Course Code", value=f"COURSE {i+1}", key=f"t1_code_{sem}_{i}").upper()
                with col2:
                    course_unit = st.number_input("Units", min_value=1, max_value=6, value=3, key=f"t1_u_{sem}_{i}")
                with col3:
                    input_mode = st.selectbox("Input By", ["Score (0-100)", "Direct Grade"], key=f"t1_mode_{sem}_{i}")
                with col4:
                    if input_mode == "Score (0-100)":
                        score = st.number_input("Score (0-100)", min_value=0, max_value=100, value=70, key=f"t1_s_{sem}_{i}")
                        if score >= 70: letter, pt = "A", 5.0
                        elif score >= 60: letter, pt = "B", 4.0
                        elif score >= 50: letter, pt = "C", 3.0
                        elif score >= 45: letter, pt = "D", 2.0
                        elif score >= 40: letter, pt = "E", 1.0
                        else: letter, pt = "F", 0.0
                        st.markdown(f"<p style='color: #4B0082; font-size: 11px; margin-top: -5px;'>↳ Grade: <b>{letter}</b> ({int(pt)} Pts)</p>", unsafe_allow_html=True)
                    else:
                        letter = st.selectbox("Choose Grade", ["A", "B", "C", "D", "E", "F"], key=f"t1_g_{sem}_{i}")
                        pt = grade_scale[letter]
                        st.markdown(f"<p style='color: #4B0082; font-size: 11px; margin-top: -5px;'>↳ Points: <b>{int(pt)} Pts</b></p>", unsafe_allow_html=True)
                
                sem_units += course_unit
                sem_points += course_unit * pt
                st.markdown("<hr style='margin: 8px 0; border-color: #eee;'>", unsafe_allow_html=True)
                
            if sem_units > 0:
                sem_gpa = sem_points / sem_units
                st.info(f"**Semester {sem + 1} GPA:** {sem_gpa:.2f} | **Total Units:** {int(sem_units)}")
                grand_total_units += sem_units
                grand_total_points += sem_points

    if grand_total_units > 0:
        calc_cgpa = grand_total_points / grand_total_units
        st.markdown("---")
        st.subheader("📷 Academic Standing Summary")
        
        st.markdown(f"""
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
        
        # Share & Export Feature (.TXT Report File Generator)
        degree_txt = "First Class" if calc_cgpa >= 4.5 else ("Second Class Upper" if calc_cgpa >= 3.5 else ("Second Class Lower" if calc_cgpa >= 2.4 else "Third Class/Pass"))
        report_data = (
            f"=== PCA ACADEMIC STANDING REPORT ===\n"
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
        
        # Save History Trigger
        if st.session_state["current_user"] is not None:
            if st.button("💾 Save Calculation to Account History"):
                entry = {"dept": department, "cgpa": f"{calc_cgpa:.2f}", "units": int(grand_total_units)}
                st.session_state["user_history"][st.session_state["current_user"]].append(entry)
                st.success("Result added to your dashboard history tab successfully!")
        else:
            st.caption("💡 Tip: Create an account or sign in on the top right to save this computation permanently.")

# TAB 2: PREDICTOR MODIFICATIONS
with tab2:
    st.markdown("<h2>🎯 Target & 'What-If' Predictor</h2>", unsafe_allow_html=True)
    st.subheader("📈 Future Target Calculator")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        curr_cgpa = st.number_input("Your Current CGPA Baseline", min_value=0.0, max_value=5.0, value=3.42, step=0.01)
        curr_units = st.number_input("Your Earned Credit Units to Date", min_value=1, max_value=200, value=68, step=1)
        average_units_per_semester = st.number_input("Average Units Per Upcoming Semester", min_value=10, max_value=30, value=20)
    with col_t2:
        target_cgpa = st.selectbox("Desired Class Target", [4.50, 3.50, 2.40], format_func=lambda x: f"{x:.2f} (First Class)" if x==4.50 else (f"{x:.2f} (Second Class Upper)" if x==3.50 else f"{x:.2f} (Second Class Lower)"))
        remaining_semesters = st.number_input("Semesters Remaining until graduation", min_value=1, max_value=8, value=4, step=1)
        
    if st.button("Calculate Needed Target Performance"):
        current_total_gp = curr_cgpa * curr_units
        estimated_future_units = remaining_semesters * average_units_per_semester
        total_final_units = curr_units + estimated_future_units
        required_grand_gp = target_cgpa * total_final_units
        needed_future_gp = required_grand_gp - current_total_gp
        required_average_gpa = needed_future_gp / estimated_future_units
        
        st.markdown("#### **Prediction Metric:**")
        if required_average_gpa > 5.0:
            st.error(f"Mathematically impossible. Hitting {target_cgpa:.2f} in {remaining_semesters} semesters requires a continuous semester average GPA of {required_average_gpa:.2f}.")
        elif required_average_gpa < 1.0:
            st.success(f"Extremely safe! Maintain a tiny base GPA of just **{max(required_average_gpa, 1.0):.2f}** per term to clear your goal line.")
        else:
            st.warning(f"🎯 You must lock down a clear average GPA of **{required_average_gpa:.2f}** across your next **{remaining_semesters} semesters** to successfully graduate inside your targeted threshold.")

# TAB 3: ADVISER
with tab3:
    st.markdown("<h2>🧠 Smart Academic Adviser</h2>", unsafe_allow_html=True)
    user_status_gpa = st.number_input("Enter your baseline CGPA for quick directive diagnostics:", min_value=0.0, max_value=5.0, value=3.55, key="adv_input")
    
    st.markdown("#### **Strategic Diagnostic Directives:**")
    if user_status_gpa >= 4.50:
        st.markdown("- **Protect Core Multipliers:** Isolate heavy credit load units. Small variations drop high grade parameters far quicker than tracking minor auxiliary components.")
    elif user_status_gpa >= 3.50:
        st.markdown("- **Zone Threshold Management:** To stay protected inside **Second Class Upper**, keep standard grades at minimum 'C' structures in major foundational sequences. Volatile credit shifts require multiple back-to-back 'A' scores to offset.")
    else:
        st.markdown("- **Remedial Recovery Blueprint:** Tackle core dependencies early. Elevating baseline grades to 'C' or 'B' classes delivers the absolute highest statistical acceleration vector for lower bands.")

# TAB 4: SAVED DATA VAULT
with tab4:
    st.markdown("<h2>💾 Local Profile History</h2>", unsafe_allow_html=True)
    if st.session_state["current_user"] is None:
        st.info("Log in using the panel at the top right to open your persistent history tab.")
    else:
        history_list = st.session_state["user_history"].get(st.session_state["current_user"], [])
        if not history_list:
            st.write("No saved calculations found for this login session yet. Go run a computation in Tab 1 and hit save!")
        else:
            for index, item in enumerate(history_list):
                st.markdown(f"📦 **Log Checkpoint #{index+1}** | Department: `{item['dept']}` | Computed CGPA: **{item['cgpa']}** | Evaluated Load: `{item['units']} Credits`")

# Standardized Global Footer
st.markdown("""
    <div class="platform-footer">
        <p style='font-weight: bold; color: #4B0082; margin-bottom: 2px;'>Physical Sciences Academic Companion (PCA)</p>
        <p style='font-size: 12px; color: #777; margin-top: 0;'>Developed by Pedro and Team</p>
    </div>
""", unsafe_allow_html=True)
