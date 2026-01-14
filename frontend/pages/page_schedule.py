import streamlit as st
from typing import Dict, Any
from PIL import Image
import time
import json
from services.utils import calculate_image_hash
from services.conversation_restore import restore_conversation_by_hash
from services.image_validation import validate_prescription
from services.extraction_service import perform_extraction
from scheduler.readiness import calculate_schedule_readiness
from scheduler.pdf_export import generate_schedule_pdf
from frontend.schedule_ui import (
    render_clarification_form, 
    render_schedule_table, 
    render_schedule_transparency
)
from frontend.session_utils import load_into_session

def render_schedule_page(model_config: Dict[str, Any], sidebar_file: Any):
    """Page 2 orchestrator: Smart Prescription Schedule."""
    st.title("Smart Prescription Schedule 📅")
    st.info("Convert your prescription into a safe, easy-to-follow daily schedule.")
    
    # 1. Image Upload Gate (Standard)
    # Using a specialized key for Scheduler uploader to handle independent resets
    if "schedule_uploader_key" not in st.session_state:
        st.session_state.schedule_uploader_key = 0
        
    # Check sidebar file first (Global Uploader)
    uploaded_file = sidebar_file
    
    # If no active prescription and no sidebar file, show local upload
    if not st.session_state.get("prescription_id") and not uploaded_file:
        uploaded_file = st.file_uploader(
            "📤 Upload Prescription Image",
            type=["png", "jpg", "jpeg"],
            key=f"schedule_uploader_{st.session_state.schedule_uploader_key}"
        )
        
    # Process new upload (either from sidebar or local)
    if uploaded_file and not st.session_state.get("prescription_id"):
            image = Image.open(uploaded_file)
            img_hash = calculate_image_hash(image)
            
            with st.status("🔍 Analyzing Prescription...", expanded=True) as status:
                # CHECK FOR DUPLICATE / EXISTING RECORD
                restored = restore_conversation_by_hash(img_hash)
                
                if restored:
                    st.write("✅ Existing record found. Loading data...")
                    load_into_session(*restored)
                    status.update(label="Data Restored", state="complete")
                else:
                    st.write("🧐 Verifying image...")
                    is_valid, validation = validate_prescription(image)
                    if not is_valid:
                        st.error(f"❌ Rejected: {validation.get('reason', 'Invalid prescription')}")
                        st.stop()
                        
                    st.write("🪄 Running extraction pipeline...")
                    p_id, analysis = perform_extraction(image, st.session_state.vision_chain)
                    load_into_session(p_id, img_hash, image, analysis, [])
                    status.update(label="Initial Extraction Complete", state="complete")
                    
            st.rerun()
    
    # 2. Main Workflow Area
    if st.session_state.get("prescription_id"):
        extraction = st.session_state.active_analysis["extraction"]
        audit_data = st.session_state.active_analysis["audit"]
        
        # Check Readiness
        readiness = calculate_schedule_readiness(extraction)
        
        # State: Needs Clarification
        if not readiness["is_ready"]:
            overrides = render_clarification_form(readiness)
            if overrides:
                # MERGE Human Overrides into Extraction
                for med_name, fields in overrides.items():
                    for med in extraction["medicines"]:
                        if med.get("name") == med_name:
                            med.update(fields)
                            med["confidence"] = 1.0 # Force human truth
                
                # Persist merged data
                from db.prescriptions import update_prescription_data
                update_prescription_data(st.session_state.prescription_id, extraction, audit_data)
                
                st.success("Human clarification merged. Ready to generate schedule.")
                st.session_state.schedule_generated = False # Trigger regen
                st.rerun()
            
            # Allow reset even from form state
            st.divider()
            if st.button("🔄 Start New Schedule", key="reset_from_form"):
                st.session_state.prescription_id = None
                st.session_state.active_img_hash = None
                st.session_state.schedule_generated = False
                st.session_state.schedule_uploader_key += 1
                st.rerun()
        
        # State: Ready -> Generate Table
        else:
            # Generate the actual schedule JSON if not already done
            if not st.session_state.get("schedule_generated"):
                with st.spinner("⏳ Synthesizing your daily timeline..."):
                    schedule_data = st.session_state.vision_chain.generate_final_schedule(extraction)
                    st.session_state.final_schedule = schedule_data.get("schedule", [])
                    st.session_state.schedule_generated = True
            
            # Show Table & Timeline
            render_schedule_table(st.session_state.final_schedule)
            
            # Export Section
            st.divider()
            col1, col2 = st.columns([1, 2])
            with col1:
                pdf_bytes = generate_schedule_pdf(st.session_state.final_schedule)
                st.download_button(
                    label="📥 Download Schedule as PDF",
                    data=pdf_bytes,
                    file_name=f"medication_schedule_{time.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            
            # New Schedule Button
            if st.button("🔄 Start New Schedule"):
                st.session_state.prescription_id = None
                st.session_state.active_img_hash = None
                st.session_state.schedule_generated = False
                st.session_state.schedule_uploader_key += 1
                st.rerun()

        # Sidebar Panel
        render_schedule_transparency(
            readiness, 
            st.session_state.get("human_overrides", {}), 
            st.session_state.vision_chain.qubrid_client.model_name
        )
    else:
        st.write("Please upload a prescription image to begin.")
