import streamlit as st
from fpdf import FPDF
import os
import requests
from datetime import datetime
from PIL import Image

# ==========================================
# 1. CONFIGURATION & CORPORATE CONSTANTS
# ==========================================
FMCO_LOGO = "FMCO-Logo-2.png"
QIDDIYA_LOGO = "images (1).png"

# 🔗 Google Sheets Web App URL
GOOGLE_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxaHygGj3K14MJrlP5HNa9zmIbl4CzSgaIio0VnRh_rc3F2gL43aYqcnvzRsDhaSbnq/exec"

# 📁 Root folder where all departure PDFs will be saved
BASE_REPORTS_FOLDER = "Departure_Reports"

# ==========================================
# 2. FOLDER STRUCTURE BUILDER
# ==========================================
def get_report_save_path(occupant_name: str, timestamp: datetime) -> tuple[str, str]:
    """
    Returns (folder_path, full_file_path) for the PDF.

    Structure:
        Departure_Reports/
            2025-06/              ← Year-Month
                15-June-2025/     ← Day folder
                    Departure_Report_Noor_20250615_143022.pdf
    """
    month_folder  = timestamp.strftime("%Y-%m")           # e.g. "2025-06"
    day_folder    = timestamp.strftime("%d-%B-%Y")        # e.g. "15-June-2025"
    safe_name     = occupant_name.replace(" ", "_")
    filename      = f"Departure_Report_{safe_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"

    folder_path   = os.path.join(BASE_REPORTS_FOLDER, month_folder, day_folder)
    os.makedirs(folder_path, exist_ok=True)

    return folder_path, os.path.join(folder_path, filename)

# ==========================================
# 3. DATABASE LOGGING FUNCTION (GOOGLE SHEETS)
# ==========================================
def log_to_google_sheet(data_dict):
    try:
        response = requests.post(GOOGLE_WEBAPP_URL, json=data_dict, timeout=10)
        if response.status_code == 200:
            st.success("💾 Records logged to Live Google Sheet database.")
        else:
            st.warning("⚠️ Form processed locally. Server response delayed.")
    except Exception as e:
        st.warning(f"Report secured locally. Cloud sync pending: {e}")

# ==========================================
# 4. HIGH-FIDELITY PDF GENERATION ENGINE
# ==========================================
class DepartureReportPDF(FPDF):
    def __init__(self, room_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_type = room_type

    def header(self):
        if os.path.exists(FMCO_LOGO):
            self.image(FMCO_LOGO, x=14, y=12, w=32)
        if os.path.exists(QIDDIYA_LOGO):
            self.image(QIDDIYA_LOGO, x=164, y=11, w=32)

        self.ln(16)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(14, 56, 74)
        self.cell(0, 8, "RESIDENT DEPARTURE & INSPECTION REPORT", ln=True, align="C")

        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 4, f"Generated automatically on: {current_time}", ln=True, align="C")
        self.ln(4)

        self.set_draw_color(14, 56, 74)
        self.set_line_width(0.8)
        self.line(12, self.get_y(), 198, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | FMCO Operations Logistics Hub", align="C")

    def section_heading(self, label):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(14, 56, 74)
        self.cell(0, 6, f"  {label}", ln=True, fill=True)
        self.ln(2)

# ==========================================
# 5. PDF BUILDER
# ==========================================
def build_pdf(pdf_save_path, occupant_name, occupant_id, building_no, room_no,
              room_type, departure_type, remarks,
              resident_signature, inspector_signature,
              door_status, wall_status, floor_status, window_status,
              ac_status, light_status, bed_status, wardrobe_status,
              drainage_status, heater_status, temp_photo_paths):

    pdf = DepartureReportPDF(room_type=room_type)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- SECTION 1: METADATA GRID ---
    pdf.section_heading("1. Occupant & Operational Metadata")
    pdf.set_fill_color(245, 245, 245)

    rows = [
        ("Occupant Name:", occupant_name,  "Resident ID:", occupant_id),
        ("Building No:",   building_no,     "Room No:",     room_no),
        ("Allocation Type:", room_type,     "Departure Action:", departure_type),
    ]
    for label1, val1, label2, val2 in rows:
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(38, 7, label1, border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(57, 7, f" {val1}", border=1)
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(35, 7, label2, border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(56, 7, f" {val2}", border=1, ln=True)

    pdf.set_text_color(0, 0, 0); pdf.ln(5)

    # --- SECTION 2: INFRASTRUCTURE CHECKLIST ---
    pdf.section_heading("2. Facility Infrastructure Checklist Evaluations")
    pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(140, 140, 140)
    pdf.cell(120, 6, "Evaluated Operational Asset Category", border=1, fill=True)
    pdf.cell(66, 6, "Status Verification", border=1, ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)

    checklist = [
        ("Main Door, Locks & Handles",                door_status),
        ("Wall Condition & Paint Protection",          wall_status),
        ("Primary Flooring & Baseboards",             floor_status),
        ("Windowpanes & Latches",                     window_status),
        ("Air Conditioning (AC) Unit & Remote",       ac_status),
        ("Lighting Fixtures & Electrical Switches",   light_status),
        ("Bedframe & Mattress Condition",             bed_status),
        ("Wardrobe, Shelving & Cabinet Hinges",       wardrobe_status),
        ("Bathroom Drainage & Plumbing Assets",       drainage_status),
        ("Water Heater Functionality",                heater_status),
    ]
    pdf.set_font("Helvetica", "", 9)
    for asset, status in checklist:
        pdf.cell(120, 6, f" {asset}", border=1)
        color = (34, 139, 34) if "Pass" in status else (178, 34, 34)
        pdf.set_text_color(*color)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(66, 6, f" {status}", border=1, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
    pdf.ln(5)

    # --- SECTION 3: REMARKS ---
    pdf.section_heading("3. Additional Field Inspection Remarks")
    pdf.set_font("Helvetica", "", 9); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, f" {remarks if remarks.strip() else 'No structural deficiencies or critical anomalies noted at evaluation timestamp.'}", border=1)
    pdf.ln(5)

    # --- SECTION 4: SIGNATURES ---
    pdf.section_heading("4. Signatures & Attestation")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(93, 5, "Resident Signature Confirmation:", ln=False)
    pdf.cell(93, 5, "Lead Inspector Verification Authorization:", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
    pdf.cell(28, 10, "Resident Name:", border='B', ln=False)
    pdf.set_font("Helvetica", "I", 11); pdf.set_text_color(34, 139, 34)
    pdf.cell(60, 10, f"  /s/ {resident_signature}", border='B', ln=False)
    pdf.cell(10, 10, "", ln=False)
    pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
    pdf.cell(28, 10, "Inspector Name:", border='B', ln=False)
    pdf.set_font("Helvetica", "I", 11); pdf.set_text_color(0, 102, 204)
    pdf.cell(60, 10, f"  /s/ {inspector_signature}", border='B', ln=True)
    pdf.ln(10)

    # --- SECTION 5: PHOTOS ---
    if temp_photo_paths:
        pdf.section_heading("5. Attached Room Condition Media")
        pdf.ln(2)
        for path in temp_photo_paths:
            if os.path.exists(path):
                if pdf.get_y() + 85 > 270:
                    pdf.add_page()
                else:
                    pdf.ln(2)
                pdf.image(path, x=45, y=pdf.get_y(), w=120)
                pdf.set_y(pdf.get_y() + 85)

    pdf.output(pdf_save_path)

# ==========================================
# 6. STREAMLIT WEB INTERFACE
# ==========================================
st.set_page_config(page_title="Departure Inspection Form", page_icon="📝", layout="centered")

logo_col1, logo_col2, logo_col3 = st.columns([1.2, 2, 1.2])
with logo_col1:
    if os.path.exists(FMCO_LOGO): st.image(FMCO_LOGO, width=120)
with logo_col2:
    st.markdown(
        "<h2 style='text-align:center;color:#0E384A;margin-top:15px;"
        "font-size:24px;font-weight:bold;'>Departure Inspection Report</h2>",
        unsafe_allow_html=True
    )
with logo_col3:
    if os.path.exists(QIDDIYA_LOGO): st.image(QIDDIYA_LOGO, width=120)

st.markdown("---")


with st.form("departure_form", clear_on_submit=True):
    st.subheader("🏢 Location & Occupant Core Attributes")
    col1, col2 = st.columns(2)
    with col1:
        occupant_name = st.text_input("Occupant Full Name", placeholder="e.g. Shadab")
        building_no   = st.text_input("Building Number",    placeholder="e.g. C02")
    with col2:
        occupant_id   = st.text_input("Resident ID / Serial", placeholder="e.g. 1234")
        room_no       = st.text_input("Room Number",          placeholder="e.g. 112")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        room_type = st.radio("**Room Allocation Type**",
                             ["Single Room", "Shared Room"], index=0, horizontal=True)
    with col_r2:
        departure_type = st.radio("**Departure Action Classification**",
                                  ["Internal Transfer", "Check-Out from Camp"], index=0, horizontal=True)

    st.markdown("---")
    st.subheader("🔍 Facility Infrastructure Checklist")

    door_status     = st.radio("**Main Door, Locks & Handles**",                  ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    wall_status     = st.radio("**Wall Condition & Paint Protection**",            ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    floor_status    = st.radio("**Primary Flooring & Baseboards**",               ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    window_status   = st.radio("**Windowpanes & Latches**",                       ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    ac_status       = st.radio("**Air Conditioning (AC) Unit & Remote**",         ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    light_status    = st.radio("**Lighting Fixtures & Electrical Switches**",     ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    bed_status      = st.radio("**Bedframe & Mattress Condition**",               ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    wardrobe_status = st.radio("**Wardrobe, Shelving & Cabinet Hinges**",         ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    drainage_status = st.radio("**Bathroom Drainage & Plumbing Assets**",         ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    heater_status   = st.radio("**Water Heater Functionality**",                  ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)

    st.markdown("---")
    uploaded_photos = st.file_uploader("Upload Room Condition Photos (Optional)",
                                       type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    remarks = st.text_area("Additional Field Observations")

    col3, col4 = st.columns(2)
    with col3: resident_signature  = st.text_input("Resident Signature (Type Name)")
    with col4: inspector_signature = st.text_input("Lead Inspector Signature (Type Name)")

    st.markdown("---")
    submit_button = st.form_submit_button("✅ Submit & Save Report")

# ==========================================
# 7. REPORT SUBMISSION PROCESSING
# ==========================================
if submit_button:
    if not occupant_name or not building_no or not room_no or not inspector_signature:
        st.error("❌ Error: Please fill in all mandatory fields (Name, Building, Room, Inspector Signature).")
    else:
        now = datetime.now()

        # ── Save temp photos ──────────────────────────────────
        temp_photo_paths = []
        if uploaded_photos:
            for idx, uploaded_photo in enumerate(uploaded_photos):
                path = f"temp_upload_{now.strftime('%Y%m%d_%H%M%S')}_{idx}.png"
                Image.open(uploaded_photo).save(path)
                temp_photo_paths.append(path)

        # ── Build folder path & PDF ───────────────────────────
        folder_path, pdf_save_path = get_report_save_path(occupant_name, now)

        build_pdf(
            pdf_save_path, occupant_name, occupant_id, building_no, room_no,
            room_type, departure_type, remarks,
            resident_signature, inspector_signature,
            door_status, wall_status, floor_status, window_status,
            ac_status, light_status, bed_status, wardrobe_status,
            drainage_status, heater_status, temp_photo_paths
        )

        # ── Log to Google Sheets ──────────────────────────────
        record_data = {
            "Timestamp":           now.strftime("%Y-%m-%d %H:%M:%S"),
            "Occupant_Name":       occupant_name,
            "Resident_ID":         occupant_id,
            "Building_Number":     building_no,
            "Room_Number":         room_no,
            "Room_Type":           room_type,
            "Departure_Type":      departure_type,
            "Remarks":             remarks,
            "Resident_Signature":  resident_signature,
            "Inspector_Signature": inspector_signature,
            "Door_Status":         door_status,
            "Wall_Status":         wall_status,
            "Floor_Status":        floor_status,
            "Window_Status":       window_status,
            "AC_Status":           ac_status,
            "Light_Status":        light_status,
            "Bed_Status":          bed_status,
            "Wardrobe_Status":     wardrobe_status,
            "Drainage_Status":     drainage_status,
            "Heater_Status":       heater_status,
            "PDF_Path":            pdf_save_path,   # extra column so you can trace the file
        }
        log_to_google_sheet(record_data)

        # ── Success feedback + download button ────────────────
        st.success(
            f"✅ Report saved successfully!\n\n"
            f"📁 Location: `{pdf_save_path}`"
        )

        with open(pdf_save_path, "rb") as f:
            st.download_button(
                label="⬇️ Download This Report PDF",
                data=f,
                file_name=os.path.basename(pdf_save_path),
                mime="application/pdf"
            )

        # ── Cleanup temp images ───────────────────────────────
        for path in temp_photo_paths:
            if os.path.exists(path):
                os.remove(path)
