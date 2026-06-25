import streamlit as st

st.set_page_config(page_title="PCA_CGPA CALCULATOR", page_icon="🎓", layout="centered")

st.title("🎓 PCA_CGPA CALCULATOR")
st.write("Calculate your Semester GPAs and Cumulative CGPA across multiple semesters instantly!")

# Grade mapping for Nigerian universities (5.0 scale)
grade_map = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}

# Step 1: Ask how many semesters total
num_semesters = st.number_input(
    "How many semesters do you want to calculate for?", 
    min_value=1, max_value=12, value=2, step=1
)

st.markdown("---")

grand_total_units = 0
grand_total_points = 0

# Step 2: Loop through each semester dynamically using expanders
for sem in range(int(num_semesters)):
    with st.expander(f"📅 Semester {sem + 1} Details", expanded=(sem == 0)):
        num_courses = st.number_input(
            f"How many courses for Semester {sem + 1}?", 
            min_value=1, max_value=20, value=5, step=1, key=f"sem_num_c_{sem}"
        )
        
        sem_units = 0
        sem_points = 0
        
        st.markdown(" ")
        
        # Grid input for courses within this specific semester
        for i in range(int(num_courses)):
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.text_input(f"Course Code", placeholder="e.g., CHM301", key=f"code_{sem}_{i}")
            
            with col2:
                course_unit = st.number_input(f"Units", min_value=1, max_value=6, value=3, step=1, key=f"unit_{sem}_{i}")
                
            with col3:
                grade = st.selectbox(f"Grade", list(grade_map.keys()), key=f"grade_{sem}_{i}")
                
            sem_units += course_unit
            sem_points += course_unit * grade_map[grade]
            
        # Per-semester calculation summary inside the expander
        if sem_units > 0:
            sem_gpa = sem_points / sem_units
            st.info(f"**Semester {sem + 1} GPA:** {sem_gpa:.2f} | **Units:** {int(sem_units)}")
            
            # Accumulate into overall grand totals
            grand_total_units += sem_units
            grand_total_points += sem_points

st.markdown("---")
st.subheader("📊 Cumulative Final Results")

# Step 3: Compute final Cumulative CGPA across all entered semesters
if grand_total_units > 0:
    cgpa = grand_total_points / grand_total_units
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric(label="Total Cumulative Units", value=int(grand_total_units))
    col_res2.metric(label="Final Cumulative CGPA", value=f"{cgpa:.2f} / 5.00")
    
    # Class of Degree classification matching university standards
    if cgpa >= 4.50:
        st.success("🔥 Outstanding performance! First Class Honours.")
    elif cgpa >= 3.50:
        st.info("👍 Excellent work! Second Class Honours (Upper Division).")
    elif cgpa >= 2.40:
        st.warning("👌 Good standing! Second Class Honours (Lower Division).")
    elif cgpa >= 1.50:
        st.warning("📚 Third Class Standing. Keep putting in effort!")
    else:
        st.error("⚠️ Pass/Academic Warning level. Focus hard on the upcoming sessions!")
else:
    st.write("Fill in your course details above to see your final cumulative result.")
