def get_dept_prefix(department):
    """FIX 6: Dynamically maps department options to official class prefixes."""
    prefix_map = {
        "Computer Science": "CSC",
        "Mathematics": "MTH",
        "Physics": "PHY",
        "Chemistry": "CHM",
        "Statistics": "STA",
        "Industrial Chemistry": "ICH"
    }
    return prefix_map.get(department, "CHM")

def get_class_badge(cgpa):
    """FIX 7: Returns premium HTML badges for official degree classifications."""
    if cgpa >= 4.50:
        return "<span style='background-color:#D4AF37; color:black; padding:4px 10px; border-radius:10px; font-weight:bold;'>First Class</span>"
    elif cgpa >= 3.50:
        return "<span style='background-color:#C0C0C0; color:black; padding:4px 10px; border-radius:10px; font-weight:bold;'>Second Class Upper (2:1)</span>"
    elif cgpa >= 2.40:
        return "<span style='background-color:#CD7F32; color:white; padding:4px 10px; border-radius:10px; font-weight:bold;'>Second Class Lower (2:2)</span>"
    elif cgpa >= 1.50:
        return "<span style='background-color:#A9A9A9; color:white; padding:4px 10px; border-radius:10px; font-weight:bold;'>Third Class</span>"
    else:
        return "<span style='background-color:#FF6347; color:white; padding:4px 10px; border-radius:10px; font-weight:bold;'>Pass/Fail Standing</span>"