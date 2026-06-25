import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="PCA_CGPA CALCULATOR", 
    page_icon="🎓", 
    layout="centered"
)

# Premium Purple & Gold Theme Custom Styling
custom_css = """
<style>
    .main { background-color: #fafafa; }
    h1 { color: #4B0082; text-align: center; font-weight: 800; margin-bottom: 5px; }
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
    .danger-zone { background-color: #FFC0CB; color: #D8000C; }
    
    .result-card {
        background: linear-gradient(135deg, #4B0082 0%, #30005C 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(75,0,130,0.2);
        text-align: center;
        margin-top: 20px;
    }
    .metric-val { font-size: 42px; font-weight: bold; color: #D4AF37; }
    .campaign-footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 25px;
        border-top: 2px dashed #4B0082;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Multi-Semester Calculator", "🎯 Target & 'What-If' Predictor", "🧠 Smart Academic Adviser"])

# Grade to Points Map
grade_scale = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}

def get_zone_badge(cgpa):
    if cgpa >= 4.50: return '<div class="zone-badge first-class">🏆 First Class Zone</div>'
    elif cgpa >= 3.50: return '<div class="zone-badge upper-division">🔥 2:1 Zone</div>'
    elif cgpa >= 2.40: return '<div class="zone-badge lower-division">📈 2:2 Zone</div>'
    else: return '<div class="zone-badge danger-zone">⚠️ Danger Zone</div>'

# TAB 1: MULTI-SEMESTER CALCULATOR (UNIVERSAL ACCESS)
with tab1:
    st.markdown("<h1>🎓 PCA_CGPA CALCULATOR</h1>", unsafe_allow_html=True)
    st.write("Calculate your detailed Semester GPAs and Cumulative CGPA across any department.")
    
    num_semesters = st.number_input("How many semesters are you calculating for?", min_value=1, max_value=12, value=2, step=1, key="main_sem_input")
    
    grand_total_units = 0
    grand_total_points = 0
    
    for sem in range(int(num_semesters)):
        with st.expander(f"📅 Semester {sem + 1} Details", expanded=(sem == 0)):
            num_courses = st.number_input(f"Number of courses in Semester {sem + 1}", min_value=1, max_value=15, value=5, key=f"num_c_{sem}")
            
            sem_units = 0
            sem_points = 0
            
            for i in range(int(num_courses)):
                st.markdown(f"**Course #{i+1}**")
                col1, col2, col3, col4 = st.columns([3, 1.5, 2, 2.5])
                
                with col1:
                    # Open Text Input allows any student to type any code (MTH, PHY, CHM, CSC, etc.)
                    course_code = st.text_input("Course Code", value=f"COURSE {i+1}", key=f"c_code_{sem}_{i}")
                
                with col2:
                    course_unit = st.number_input("Units", min_value=1, max_value=6, value=3, key=f"u_val_{sem}_{i}")
                
                with col3:
                    input_mode = st.selectbox("Input By", ["Score (0-100)", "Direct Grade"], key=f"mode_{sem}_{i}")
                    
                with col4:
                    if input_mode == "Score (0-100)":
                        score = st.number_input("Score (0-100)", min_value=0, max_value=100, value=70, key=f"s_val_{sem}_{i}")
                        # Score Conversion Logic
                        if score >= 70: letter, pt = "A", 5.0
                        elif score >= 60: letter, pt = "B", 4.0
                        elif score >= 50: letter, pt = "C", 3.0
                        elif score >= 45: letter, pt = "D", 2.0
                        elif score >= 40: letter, pt = "E", 1.0
                        else: letter, pt = "F", 0.0
                        st.markdown(f"<p style='color: #6A0DAD; font-size: 11px; margin-top: -5px;'>↳ Calculated: <b>Grade {letter}</b> ({int(pt)} Pts)</p>", unsafe_allow_html=True)
                    else:
                        letter = st.selectbox("Choose Grade", ["A", "B", "C", "D", "E", "F"], key=f"g_val_{sem}_{i}")
                        pt = grade_scale[letter]
                        st.markdown(f"<p style='color: #6A0DAD; font-size: 11px; margin-top: -5px;'>↳ Manual: <b>{int(pt)} Points</b> Assigned</p>", unsafe_allow_html=True)
                
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
        st.subheader("📷 Screenshot-Ready Results Card")
        
        st.markdown(f"""
            <div class="result-card">
                <h2 style='color: #D4AF37; margin-bottom: 2px;'>NATIONAL ASSOCIATION OF PHYSICAL SCIENCE STUDENTS</h2>
                <p style='margin-top: 0; font-size: 13px; opacity: 0.8;'>EKITI STATE UNIVERSITY CHAPTER</p>
                <hr style='border-color: rgba(255,255,255,0.15);'>
                <p style='font-size: 16px; margin-bottom: 0; letter-spacing: 1px;'>OFFICIAL STANDING</p>
                <div class="metric-val">{calc_cgpa:.2f} / 5.00</div>
                {get_zone_badge(calc_cgpa)}
                <p style='font-size: 13px; opacity: 0.8; margin-top: 15px;'>Total Evaluated Credit Units: <b>{int(grand_total_units)}</b></p>
            </div>
        """, unsafe_allow_html=True)

# TAB 2: TARGET & "WHAT-IF" PREDICTOR
with tab2:
    st.markdown("<h2>🎯 Target & 'What-If' Predictor</h2>", unsafe_allow_html=True)
    
    st.subheader("📈 Future Target Calculator")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        curr_cgpa = st.number_input("Your Current CGPA", min_value=0.0, max_value=5.0, value=3.42, step=0.01)
        curr_units = st.number_input("Your Earned Credit Units so far", min_value=1, max_value=200, value=68, step=1)
    with col_t2:
        target_cgpa = st.selectbox("Your Desired Graduation Target", [4.50, 3.50, 2.40], format_func=lambda x: f"{x:.2f} (First Class)" if x==4.50 else (f"{x:.2f} (2:1)" if x==3.50 else f"{x:.2f} (2:2)"))
        remaining_semesters = st.number_input("Semesters left until graduation", min_value=1, max_value=8, value=4, step=1)
        
    if st.button("Calculate Needed Performance"):
        current_total_gp = curr_cgpa * curr_units
        estimated_future_units = remaining_semesters * 20 
        total_final_units = curr_units + estimated_future_units
        required_grand_gp = target_cgpa * total_final_units
        needed_future_gp = required_grand_gp - current_total_gp
        required_average_gpa = needed_future_gp / estimated_future_units
        
        st.markdown("#### **Prediction Verdict:**")
        if required_average_gpa > 5.0:
            st.error(f"Mathematically, reaching {target_cgpa:.2f} isn't possible in {remaining_semesters} semesters with an average 20-unit load. Focus on maximizing every upcoming class!")
        elif required_average_gpa < 1.0:
            st.success(f"You are completely on track! Maintain an average semester GPA of just **{max(required_average_gpa, 1.0):.2f}** to cross your target.")
        else:
            st.warning(f"🎯 You need to hit an average GPA of **{required_average_gpa:.2f}** across each of your next **{remaining_semesters} semesters** to graduate with your target standing.")

    st.markdown("---")
    st.subheader("🎲 Addictive 'What-If' Simulator")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        sim_cgpa = st.number_input("Current CGPA Baseline", min_value=0.0, max_value=5.0, value=3.55, key="sim_cgpa")
        sim_units = st.number_input("Current Earned Units Baseline", min_value=1, max_value=200, value=75, key="sim_units")
    with col_w2:
        st.markdown("**Simulate Grades to add:**")
        num_as = st.number_input("Number of 'A' Grades (3 Units each)", min_value=0, max_value=10, value=3)
        num_bs = st.number_input("Number of 'B' Grades (3 Units each)", min_value=0, max_value=10, value=2)
        num_cs = st.number_input("Number of 'C' Grades (3 Units each)", min_value=0, max_value=10, value=0)

    sim_added_units = (num_as + num_bs + num_cs) * 3
    sim_added_points = (num_as * 5.0 * 3) + (num_bs * 4.0 * 3) + (num_cs * 3.0 * 3)
    
    if sim_added_units > 0:
        new_sim_cgpa = ((sim_cgpa * sim_units) + sim_added_points) / (sim_units + sim_added_units)
        st.metric(label="Simulated New Cumulative CGPA", value=f"{new_sim_cgpa:.2f} / 5.00", delta=f"{new_sim_cgpa - sim_cgpa:+.3f}")

# TAB 3: SMART ACADEMIC ADVISER
with tab3:
    st.markdown("<h2>🧠 Smart Academic Adviser</h2>", unsafe_allow_html=True)
    
    user_status_gpa = st.number_input("Enter your current CGPA to get advisor insights:", min_value=0.0, max_value=5.0, value=3.55, key="adviser_input")
    
    st.markdown("#### **Advisor Directives:**")
    if user_status_gpa >= 4.50:
        st.markdown("- **Protect Core Weights:** Prioritize high-unit core modules (like 4-unit or 5-unit foundational courses). Dropping marks here impacts your baseline standing much quicker than electives.")
        st.markdown("- **Session Strategy:** Allocate targeted study blocks to upcoming experimental, computational, or advanced structural series.")
    elif user_status_gpa >= 3.50:
        st.markdown("- **Risk Warning:** To securely stay in the **2:1 Zone**, avoid dropping below a 'C' grade in any 3-unit or 4-unit core module. Low grades in heavy multipliers require multiple 'A's to balance out.")
        st.markdown("- **High Impact Target:** Scoring an 'A' in crucial 3-unit or 4-unit departmental courses will lift your CGPA upward twice as fast as general options.")
    else:
        st.markdown("- **Recovery Road Map:** Prioritize clearing any past backlogs. Converting low scores into steady 'C' or 'B' grades provides the largest mathematical jump to your overall average standing.")

# Campaign Footer
st.markdown("""
    <div class="campaign-footer">
        <h2 style='color: #4B0082; margin-bottom: 2px;'>💜 PEDRO @ NAPSS LEVEL</h2>
        <p style='font-style: italic; color: #555; font-size: 15px;'><b>Leadership • Transparency • Capacity</b></p>
        <p style='color: #D4AF37; font-size: 14px; font-weight: bold;'>✨ Tell a friend to tell a friend! ✨</p>
    </div>
""", unsafe_allow_html=True)
