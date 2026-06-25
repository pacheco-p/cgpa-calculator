import streamlit as st

st.set_page_config(page_title="PCA_CGPA CALCULATOR", page_icon="🎓", layout="centered")

st.title("🎓 PCA_CGPA CALCULATOR")
st.write("Calculate your Semester GPA or Cumulative CGPA instantly. Built for everyone!")

# Grade mapping for Nigerian universities (5.0 scale)
grade_map = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}

num_courses = st.number_input("How many courses did you take?", min_value=1, max_value=20, value=5, step=1)

st.markdown("---")
st.subheader("📝 Enter Course Details")

total_units = 0
total_grade_points = 0

# Create columns for clean entry
for i in range(int(num_courses)):
    st.markdown(f"#### Course {i+1}")
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        course_code = st.text_input(f"Course Code", placeholder="e.g., MTH101", key=f"code_{i}")
    
    with col2:
        course_unit = st.number_input(f"Course Unit", min_value=1, max_value=6, value=3, step=1, key=f"unit_{i}")
        
    with col3:
        grade = st.selectbox(f"Grade Obtained", list(grade_map.keys()), key=f"grade_{i}")
        
    # Calculations
    total_units += course_unit
    total_grade_points += course_unit * grade_map[grade]
    st.markdown("---")

# Final Results
if total_units > 0:
    gpa = total_grade_points / total_units
    st.subheader("📊 Your Calculation Result")
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric(label="Total Course Units", value=int(total_units))
    col_res2.metric(label="Calculated GPA / CGPA", value=f"{gpa:.2f} / 5.00")
    
    if gpa >= 4.50:
        st.success("🔥 Excellent! First Class Standing.")
    elif gpa >= 3.50:
        st.info("👍 Great job! Second Class Upper Standing.")
    elif gpa >= 2.40:
        st.warning("👌 Good effort! Second Class Lower Standing.")
    else:
        st.error("📚 Keep pushing! You can lift this higher next semester.")
