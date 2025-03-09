import streamlit as st
import numpy as np
from src.database.database import SessionLocal
from src.services.diagnosis_service import DiagnosisService
from src.database.models import User
import json
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def render_diagnosis_form():
    st.header("New Medical Diagnosis")
    st.write("""
    Please enter the patient's medical parameters below.
    All measurements should be taken within the last 24 hours.
    """)

    with st.form("diagnosis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            glucose_level = st.number_input(
                "Glucose Level (mg/dL)",
                min_value=0.0,
                max_value=500.0,
                help="Fasting blood glucose level"
            )
            
            # Split blood pressure into systolic and diastolic
            st.write("Blood Pressure (mm Hg)")
            bp_col1, bp_col2 = st.columns(2)
            with bp_col1:
                systolic = st.number_input(
                    "Systolic",
                    min_value=70,
                    max_value=200,
                    value=120,
                    help="Upper number (systolic)"
                )
            with bp_col2:
                diastolic = st.number_input(
                    "Diastolic",
                    min_value=40,
                    max_value=130,
                    value=80,
                    help="Lower number (diastolic)"
                )
            blood_pressure = f"{systolic}/{diastolic}"
            
            skin_thickness = st.number_input(
                "Skin Thickness (mm)",
                min_value=0.0,
                max_value=100.0,
                help="Triceps skin fold thickness"
            )
            
            insulin_level = st.number_input(
                "Insulin Level (μU/ml)",
                min_value=0.0,
                max_value=1000.0,
                help="2-Hour serum insulin"
            )

        with col2:
            bmi = st.number_input(
                "BMI",
                min_value=0.0,
                max_value=100.0,
                help="Body Mass Index"
            )
            
            diabetes_pedigree = st.number_input(
                "Diabetes Pedigree Function",
                min_value=0.0,
                max_value=10.0,
                help="Diabetes mellitus history in relatives"
            )
            
            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                help="Patient's age in years"
            )

        submitted = st.form_submit_button("Get Diagnosis")
        
        if submitted:
            if not all([glucose_level, skin_thickness, 
                       insulin_level, bmi, diabetes_pedigree, age]):
                st.error("Please fill in all the fields.")
                return None
            
            return {
                "glucose_level": glucose_level,
                "blood_pressure": blood_pressure,
                "skin_thickness": skin_thickness,
                "insulin_level": insulin_level,
                "bmi": bmi,
                "diabetes_pedigree_function": diabetes_pedigree,
                "age": age
            }
    
    return None

def display_diagnosis_result(disease, confidence):
    st.success("Diagnosis Complete!")
    
    # Display results in a nice format
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Confidence Score", f"{confidence:.1f}%")
        st.write("### Predicted Condition")
        st.write(disease.name)
        
    with col2:
        st.write("### Description")
        st.write(disease.description)
        
    # Display additional information
    st.write("### Risk Factors")
    risk_factors = json.loads(disease.risk_factors)
    for factor in risk_factors:
        st.write(f"- {factor}")
        
    st.write("### Common Symptoms")
    common_symptoms = json.loads(disease.common_symptoms)
    for symptom in common_symptoms:
        st.write(f"- {symptom}")
        
    # Recommendations based on confidence score
    st.write("### Recommendations")
    if confidence >= 90:
        st.info("High confidence prediction. Please consult with a healthcare provider for confirmation.")
    elif confidence >= 70:
        st.warning("Moderate confidence prediction. Further tests may be required.")
    else:
        st.error("Low confidence prediction. Please consult with a healthcare provider for a thorough examination.")

def diagnosis_page(user: User, db: Session):
    """Diagnosis page with active database session."""
    # Initialize services
    diagnosis_service = DiagnosisService()
    
    # Render the diagnosis form
    params = render_diagnosis_form()
    
    if params:
        with st.spinner("Analyzing medical parameters..."):
            try:
                # Make prediction
                disease, confidence = diagnosis_service.predict_disease(
                    db=db,
                    params=params,
                    record_id=user.patient_record.record_id
                )
                
                # Display results
                display_diagnosis_result(disease, confidence)
                
            except Exception as e:
                st.error(f"An error occurred during diagnosis: {str(e)}")

if __name__ == "__main__":
    st.error("Please run the main application file instead.") 