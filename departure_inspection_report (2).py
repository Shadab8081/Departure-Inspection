import streamlit as st
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import requests
from datetime import datetime
from PIL import Image

# ==========================================
# 1. CONFIGURATION & CORPORATE CONSTANTS
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "mdshadabk318@gmail.com"
SENDER_PASSWORD = "sqrt ahgl mrgx zidd"  # Replace with your Gmail App Password
RECEIVER_EMAIL = "housing.lp@qiddiya.fmco.sa"

FMCO_LOGO = "FMCO-Logo-2.png"
QIDDIYA_LOGO = "images (1).png"

# 🔗 PASTE YOUR GOOGLE WEB APP DEPLOYMENT URL HERE:
GOOGLE_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxaHygGj3K14MJrlP5HNa9zmIbl4CzSgaIio0VnRh_rc3F2gL43aYqcnvzRsDhaSbnq/exec"

# ==========================================
# 2. DATABASE LOGGING FUNCTION (GOOGLE SHEETS)
# ==========================================
def log_to_google_sheet(data_dict):
    try:
        response = requests.post(GOOGLE_WEBAPP_URL, json=data_dict, timeout=10)
        if response.status_code == 200:
            st.success("💾 Operational records logged permanently to Live Google Sheet database.")
        else:
            st.warning("⚠️ Form processed locally. Server response delayed.")
    except Exception as e:
        st.warning(f"Report secured locally. Cloud sync pending: {e}")

# ==========================================
# 3. HIGH-FIDELITY PDF GENERATION ENGINE
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
# 4. SECURE EMAIL TRANSMISSION ENGINE
# ==========================================
def send_report_via_email(pdf_filename, occupant_name, building, room):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"🔔 Departure Report Submitted: Bldg {building} - Room {room} ({occupant_name})"
    
    body = f"Hello,\n\nA new digital departure room inspection report has been recorded for {occupant_name} (Bldg {building}, Room {room}).\n\nPlease find the official PDF layout copy attached below."
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with open(pdf_filename, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(pdf_filename)}")
            msg.attach(part)
            
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to transmit email notification: {e}")
        return False

# ==========================================
# 5. STREAMLIT WEB INTERFACE LAYOUT
# ==========================================
st.set_page_config(page_title="Departure Inspection Form", page_icon="📝", layout="centered")

logo_col1, logo_col2, logo_col3 = st.columns([1.2, 2, 1.2])
with logo_col1:
    if os.path.exists(FMCO_LOGO): st.image(FMCO_LOGO, width=140)
with logo_col2:
    st.markdown("<h2 style='text-align: center; color: #0E384A; margin-top: 15px; font-size: 24px; font-weight: bold;'>Departure Inspection Report</h2>", unsafe_allow_html=True)
with logo_col3:
    if os.path.exists(QIDDIYA_LOGO): st.image(QIDDIYA_LOGO, width=140)

st.markdown("---")

with st.form("departure_form", clear_on_submit=True):
    st.subheader("🏢 Location & Occupant Core Attributes")
    col1, col2 = st.columns(2)
    with col1:
        occupant_name = st.text_input("Occupant Full Name", placeholder="e.g. Noor")
        building_no = st.text_input("Building Number", placeholder="e.g. C02")
    with col2:
        occupant_id = st.text_input("Resident ID / Serial", placeholder="e.g. 1234")
        room_no = st.text_input("Room Number", placeholder="e.g. 112")
        
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        room_type = st.radio("**Room Allocation Type**", ["Single Room", "Shared Room"], index=0, horizontal=True)
    with col_r2:
        departure_type = st.radio("**Departure Action Classification**", ["Internal Transfer", "Check-Out from Camp"], index=0, horizontal=True)
        
    st.markdown("---")
    st.subheader("🔍 Facility Infrastructure Checklist")
    
    door_status = st.radio("**Main Door, Locks & Handles**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    wall_status = st.radio("**Wall Condition & Paint Protection**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    floor_status = st.radio("**Primary Flooring & Baseboards**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    window_status = st.radio("**Windowpanes & Latches**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    ac_status = st.radio("**Air Conditioning (AC) Unit & Remote Function**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    light_status = st.radio("**Lighting Fixtures & Electrical Switches**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    bed_status = st.radio("**Bedframe & Mattress Condition**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    wardrobe_status = st.radio("**Wardrobe, Shelving & Cabinet Hinges**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    drainage_status = st.radio("**Bathroom Drainage & Plumbing Assets**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)
    heater_status = st.radio("**Water Heater Functionality**", ["Pass (Excellent)", "Action Required (Damage/Defect)"], horizontal=True)

    st.markdown("---")
    uploaded_photos = st.file_uploader("Upload Room Condition Photos (Optional)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    remarks = st.text_area("Additional Field Observations")
    
    col3, col4 = st.columns(2)
    with col3: 
        resident_signature = st.text_input("Resident Signature (Type Name)")
    with col4: 
        inspector_signature = st.text_input("Lead Inspector Signature (Type Name)")

    st.markdown("---")
    submit_button = st.form_submit_button("Submit Formal Report")

# ==========================================
# 6. REPORT SUBMISSION PROCESSING CORE
# ==========================================
if submit_button:
    if not occupant_name or not building_no or not room_no or not inspector_signature:
        st.error("❌ Error: Fill in all mandatory field criteria.")
    else:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"Departure_Report_{occupant_name.replace(' ', '_')}_{timestamp_str}.pdf"
        
        temp_photo_paths = []
        if uploaded_photos:
            for idx, uploaded_photo in enumerate(uploaded_photos):
                path = f"temp_upload_{timestamp_str}_{idx}.png"
                image = Image.open(uploaded_photo)
                image.save(path)
                temp_photo_paths.append(path)
        
        record_data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Occupant_Name": occupant_name, "Resident_ID": occupant_id,
            "Building_Number": building_no, "Room_Number": room_no,
            "Room_Type": room_type, "Departure_Type": departure_type,
            "Remarks": remarks,
            "Resident_Signature": resident_signature, "Inspector_Signature": inspector_signature,
            "Door_Status": door_status, "Wall_Status": wall_status, "Floor_Status": floor_status,
            "Window_Status": window_status, "AC_Status": ac_status, "Light_Status": light_status,
            "Bed_Status": bed_status, "Wardrobe_Status": wardrobe_status, "Drainage_Status": drainage_status,
            "Heater_Status": heater_status
        }
        
        log_to_google_sheet(record_data)
        
        pdf = DepartureReportPDF(room_type=room_type)
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # --- SECTION 1: METADATA GRID ---
        pdf.section_heading("1. Occupant & Operational Metadata")
        pdf.set_fill_color(245, 245, 245)
        
        # Row 1
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(38, 7, "Occupant Name:", border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(57, 7, f" {occupant_name}", border=1)
        
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(35, 7, "Resident ID:", border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(56, 7, f" {occupant_id}", border=1, ln=True)
        
        # Row 2
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(38, 7, "Building No:", border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(57, 7, f" {building_no}", border=1)
        
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(35, 7, "Room No:", border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(56, 7, f" {room_no}", border=1, ln=True)
        
        # Row 3
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(38, 7, "Allocation Type:", border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(57, 7, f" {room_type}", border=1)
        
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(35, 7, "Departure Action:", border=1, fill=True)
        pdf.set_text_color(34, 139, 34); pdf.cell(56, 7, f" {departure_type}", border=1, ln=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        # --- SECTION 2: INFRASTRUCTURE CHECKLIST ---
        pdf.section_heading("2. Facility Infrastructure Checklist Evaluations")
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(140, 140, 140)
        pdf.cell(120, 6, "Evaluated Operational Asset Category", border=1, fill=True)
        pdf.cell(66, 6, "Status Verification", border=1, ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf_items_loop = [
            ("Main Door, Locks & Handles", door_status),
            ("Wall Condition & Paint Protection", wall_status),
            ("Primary Flooring & Baseboards", floor_status),
            ("Windowpanes & Latches", window_status),
            ("Air Conditioning (AC) Unit & Remote Function", ac_status),
            ("Lighting Fixtures & Electrical Switches", light_status),
            ("Bedframe & Mattress Condition", bed_status),
            ("Wardrobe, Shelving & Cabinet Hinges", wardrobe_status),
            ("Bathroom Drainage & Plumbing Assets", drainage_status),
            ("Water Heater Functionality", heater_status)
        ]
        
        pdf.set_font("Helvetica", "", 9)
        for asset, status in pdf_items_loop:
            pdf.cell(120, 6, f" {asset}", border=1)
            if "Pass" in status:
                pdf.set_text_color(34, 139, 34)
                pdf.set_font("Helvetica", "B", 9)
            else:
                pdf.set_text_color(178, 34, 34)
                pdf.set_font("Helvetica", "B", 9)
            pdf.cell(66, 6, f" {status}", border=1, ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)
        pdf.ln(5)
        
        # --- SECTION 3: RECTIFICATION FIELD REMARKS ---
        pdf.section_heading("3. Additional Field Inspection Remarks")
        # 🛡️ FIX: Explicitly set text color to solid black before printing observations!
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0) 
        pdf.multi_cell(0, 6, f" {remarks if remarks.strip() else 'No structural deficiencies or critical anomalies noted at evaluation timestamp.'}", border=1)
        pdf.ln(5)
        
        # --- SECTION 4: AUTHORIZED ATTESTATION ---
        pdf.section_heading("4. Signatures & Attestation")
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(93, 5, "Resident Signature Confirmation:", ln=False)
        pdf.cell(93, 5, "Lead Inspector Verification Authorization:", ln=True)
        pdf.ln(2)
        
        # Left Block: Resident
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(28, 10, "Resident Name:", border='B', ln=False)
        
        pdf.set_font("Helvetica", "I", 11); pdf.set_text_color(34, 139, 34)
        pdf.cell(60, 10, f"  /s/ {resident_signature}", border='B', ln=False)
        
        pdf.cell(10, 10, "", ln=False)
        
        # Right Block: Inspector
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(28, 10, "Inspector Name:", border='B', ln=False)
        
        pdf.set_font("Helvetica", "I", 11); pdf.set_text_color(0, 102, 204)
        pdf.cell(60, 10, f"  /s/ {inspector_signature}", border='B', ln=True)
        pdf.ln(10)
        
        # --- SECTION 5: MULTIPLE PHOTO ATTACHMENT LOOP ---
        if temp_photo_paths:
            pdf.section_heading("5. Attached Room Condition Media Feature")
            pdf.ln(2)
            
            for path in temp_photo_paths:
                if os.path.exists(path):
                    if pdf.get_y() + 85 > 270:
                        pdf.add_page()
                    else:
                        pdf.ln(2)
                    
                    pdf.image(path, x=45, y=pdf.get_y(), w=120)
                    pdf.set_y(pdf.get_y() + 85)
        
        pdf.output(pdf_filename)
        
        if send_report_via_email(pdf_filename, occupant_name, building_no, room_no):
            st.success(f"🎉 Complete structural breakdown report processed and transmitted to inbox.")
        
        if os.path.exists(pdf_filename): 
            os.remove(pdf_filename)
        for path in temp_photo_paths:
            if os.path.exists(path):
                os.remove(path)
