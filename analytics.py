import uuid
from datetime import datetime
import pandas as pd
import streamlit as st
from database import get_db_connection
from helpers import get_class_badge

def save_audit_session(username, department, cgpa, total_units, course_list):
    """FIX 4: Group records using a unique runtime Session ID to eliminate duplicate explosion."""
    conn = get_db_connection()
    cursor = conn.cursor()
    session_id = uuid.uuid4().hex
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO history (session_id, username, timestamp, department, cgpa, units)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, username, now_str, department, round(cgpa, 2), int(total_units)))
    
    for course in course_list:
        cursor.execute("""
            INSERT INTO course_history (session_id, username, semester_index, course_code, units, grade, points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, username, course["sem_idx"], course["code"], course["units"], course["grade"], course["pts"]))
        
    conn.commit()
    conn.close()
    return True

def render_dashboard(username):
    conn = get_db_connection()
    
    df_summary = pd.read_sql_query("SELECT session_id, timestamp, cgpa, units FROM history WHERE username = ? ORDER BY timestamp ASC", conn, params=(username,))
    df_courses = pd.read_sql_query("SELECT session_id, semester_index as 'Semester', course_code as 'Course', units as 'Units', grade as 'Grade' FROM course_history WHERE username = ? ORDER BY id DESC", conn, params=(username,))
    
    if df_summary.empty:
        st.info("No saved telemetry records indexed yet. Save an evaluation row inside Tab 1.")
        conn.close()
        return

    # FIX 9: Advanced Trend Metrics Engine
    latest_cgpa = df_summary["cgpa"].iloc[-1]
    highest_cgpa = df_summary["cgpa"].max()
    initial_cgpa = df_summary["cgpa"].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Current Entry", f"{latest_cgpa:.2f}")
    with col2: st.metric("Peak Historical", f"{highest_cgpa:.2f}")
    with col3: 
        st.markdown(f"<b>Current Stand</b><br>{get_class_badge(latest_cgpa)}", unsafe_allow_html=True)
    with col4:
        delta = latest_cgpa - initial_cgpa
        st.metric("Net Run Growth", f"{delta:+.2f}")

    # FIX 8: Graph with absolute timestamps
    st.subheader("📉 Historical CGPA Progression Timeline")
    df_chart = df_summary.copy()
    df_chart["timestamp"] = pd.to_datetime(df_chart["timestamp"])
    df_chart.set_index("timestamp", inplace=True)
    st.line_chart(df_chart["cgpa"])

    # FIX 5: Audit session cleanup & removals
    st.subheader("📋 Session History Logs")
    session_options = {row["session_id"]: f"{row['timestamp']} (CGPA: {row['cgpa']:.2f})" for _, row in df_summary.iterrows()}
    
    selected_session = st.selectbox("Select Academic Audit Session", list(session_options.keys()), format_func=lambda x: session_options[x])
    
    if st.button("🗑️ Delete Selected Session Snapshot"):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history WHERE session_id = ?", (selected_session,))
        conn.commit()
        st.success("Session entry dropped successfully.")
        st.rerun()
        
    filtered_courses = df_courses[df_courses["session_id"] == selected_session].drop(columns=["session_id"])
    st.dataframe(filtered_courses, use_container_width=True, hide_index=True)
    conn.close()