import streamlit as st

st.set_page_config(page_title="CGPA Calculator", page_icon="🎓", layout="centered")

st.title("🎓 Smart CGPA Calculator")
st.write("Calculate your Semester GPA or Cumulative CGPA instantly. Built for everyone!")

# Step 1: Get number of courses
num_courses = st.number_input("How many courses did you take?", min_value=1, max_value=20, value=5, step=1)

total_credit_hours = 0
total_grade_points = 0

st.write("---")
st.subheader("📝 Enter Course Details")

# Step 2: Dynamically create input rows for each course
for i in range(int(num_courses)):
    col1, col2 = st.columns(2)
    
    with col1:
        credits = st.number_input(f"Course {i+1} Credits", min_value=1.0, max_value=6.0, value=3.0, step=1.0, key=f"cr_{i}")
    with col2:
        grade_point = st.number_input(f"Course {i+1} Grade Point (e.g. A=4.0)", min_value=0.0, max_value=5.0, value=4.0, step=0.1, key=f"gp_{i}")
        
    total_grade_points += (credits * grade_point)
    total_credit_hours += credits

st.write("---")

# Step 3: Calculate and display results
if total_credit_hours > 0:
    cgpa = total_grade_points / total_credit_hours
    
    st.balloons() # Fun animation on success
    st.success(f"### 🎉 Your Final CGPA: {cgpa:.2f}")
    
    # Simple breakdown metric boxes
    c1, c2 = st.columns(2)
    c1.metric("Total Credits Earned", f"{total_credit_hours:.1f}")
    c2.metric("Total Quality Points", f"{total_grade_points:.1f}")
else:
    st.error("Total credit hours cannot be zero.")