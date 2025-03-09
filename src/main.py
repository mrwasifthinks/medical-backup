import streamlit as st
from pathlib import Path
import sys

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.database.database import SessionLocal
from src.services.auth_service import authenticate_user, create_user
from src.database.schemas import UserCreate
from frontend.pages.diagnosis import diagnosis_page
from sqlalchemy.orm import joinedload
from src.database.models import User, Diagnosis, PatientRecord

# Configure Streamlit page
st.set_page_config(
    page_title="AI Medical Diagnosis System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def refresh_user():
    """Refresh user object with a new database session."""
    if st.session_state.user:
        db = SessionLocal()
        try:
            # Load user with patient_record relationship
            user = db.query(User).options(
                joinedload(User.patient_record)
            ).filter(
                User.user_id == st.session_state.user.user_id
            ).first()
            return user, db
        except Exception as e:
            st.error(f"Error refreshing user data: {str(e)}")
            return None, db
    return None, None

def login_page():
    st.title("Welcome to AI Medical Diagnosis System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            db = get_db()
            user = authenticate_user(db, username, password)
            if user:
                st.session_state.user = user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def signup_page():
    st.title("Create New Account")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        submitted = st.form_submit_button("Sign Up")
        
        if submitted:
            try:
                db = get_db()
                user_data = UserCreate(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender
                )
                user = create_user(db, user_data)
                st.success("Account created successfully! Please login.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

def home_page():
    st.header("AI Medical Diagnosis System")
    st.write("""
    This system uses advanced machine learning algorithms to assist in medical diagnosis.
    Please select 'New Diagnosis' from the sidebar to start a new diagnosis session.
    """)
    
    # Display key features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🔍 Accurate Diagnosis")
        st.write("Using advanced ML models")
    with col2:
        st.info("⚡ Fast Results")
        st.write("Get instant predictions")
    with col3:
        st.info("📊 Detailed Reports")
        st.write("Comprehensive analysis")

def history_page():
    st.title("Diagnosis History")
    
    # Refresh user data
    user, db = refresh_user()
    if not user:
        st.error("Error loading user data")
        return
    
    if not user.patient_record:
        st.warning("No patient record found. Please complete your medical profile first.")
        return
    
    diagnoses = db.query(Diagnosis).filter(
        Diagnosis.record_id == user.patient_record.record_id
    ).order_by(Diagnosis.diagnosis_date.desc()).all()
    
    if not diagnoses:
        st.info("No previous diagnoses found.")
        return
    
    for diagnosis in diagnoses:
        with st.expander(f"Diagnosis from {diagnosis.diagnosis_date.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Confidence Score", f"{diagnosis.confidence_score:.1f}%")
                st.write(f"**Condition:** {diagnosis.disease.name}")
            with col2:
                st.write("**Status:**", diagnosis.status)
                st.write("**Model Version:**", diagnosis.model_version)
            if diagnosis.notes:
                st.write("**Notes:**", diagnosis.notes)

def profile_page():
    st.title("Patient Profile")
    
    # Refresh user data
    user, db = refresh_user()
    if not user:
        st.error("Error loading user data")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Personal Information")
        st.write(f"**Name:** {user.first_name} {user.last_name}")
        st.write(f"**Email:** {user.email}")
        st.write(f"**Gender:** {user.gender}")
    
    with col2:
        st.write("### Account Information")
        st.write(f"**Username:** {user.username}")
        st.write(f"**Account Created:** {user.created_at.strftime('%Y-%m-%d')}")
        st.write(f"**Last Updated:** {user.updated_at.strftime('%Y-%m-%d')}")

    # Medical Profile Section
    st.write("### Medical Profile")
    
    if not user.patient_record:
        st.warning("No medical profile found. Please create one below.")
    else:
        st.success("Medical profile exists. You can update it below.")

    with st.form("medical_profile_form"):
        medical_history = st.text_area(
            "Medical History",
            value=user.patient_record.medical_history if user.patient_record else "",
            help="Include any significant medical conditions or surgeries"
        )
        
        allergies = st.text_area(
            "Allergies",
            value=user.patient_record.allergies if user.patient_record else "",
            help="List any known allergies"
        )
        
        current_medications = st.text_area(
            "Current Medications",
            value=user.patient_record.current_medications if user.patient_record else "",
            help="List all current medications and dosages"
        )
        
        family_history = st.text_area(
            "Family History",
            value=user.patient_record.family_history if user.patient_record else "",
            help="Include significant family medical history"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            blood_type = st.selectbox(
                "Blood Type",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(user.patient_record.blood_type) if user.patient_record and user.patient_record.blood_type else 0
            )
            
            height = st.number_input(
                "Height (cm)",
                min_value=0.0,
                max_value=300.0,
                value=float(user.patient_record.height) if user.patient_record else 170.0
            )
        
        with col2:
            weight = st.number_input(
                "Weight (kg)",
                min_value=0.0,
                max_value=500.0,
                value=float(user.patient_record.weight) if user.patient_record else 70.0
            )
            
            emergency_contact = st.text_input(
                "Emergency Contact",
                value=user.patient_record.emergency_contact if user.patient_record else "",
                help="Name and phone number"
            )
        
        submitted = st.form_submit_button("Save Medical Profile")
        
        if submitted:
            try:
                # Create or update patient record
                if not user.patient_record:
                    patient_record = PatientRecord(
                        user_id=user.user_id,
                        medical_history=medical_history,
                        allergies=allergies,
                        current_medications=current_medications,
                        family_history=family_history,
                        blood_type=blood_type,
                        height=height,
                        weight=weight,
                        emergency_contact=emergency_contact
                    )
                    db.add(patient_record)
                else:
                    user.patient_record.medical_history = medical_history
                    user.patient_record.allergies = allergies
                    user.patient_record.current_medications = current_medications
                    user.patient_record.family_history = family_history
                    user.patient_record.blood_type = blood_type
                    user.patient_record.height = height
                    user.patient_record.weight = weight
                    user.patient_record.emergency_contact = emergency_contact
                
                db.commit()
                st.success("Medical profile saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving medical profile: {str(e)}")
                db.rollback()

def main_page():
    st.title(f"Welcome, {st.session_state.user.first_name}!")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.session_state.current_page = st.sidebar.radio(
        "Select a page",
        ["Home", "New Diagnosis", "History", "Profile"]
    )
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    # Main content based on selected page
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "New Diagnosis":
        # Pass fresh database session to diagnosis page
        user, db = refresh_user()
        if user and user.patient_record:
            diagnosis_page(user, db)
        else:
            st.error("Please complete your medical profile first")
    elif st.session_state.current_page == "History":
        history_page()
    elif st.session_state.current_page == "Profile":
        profile_page()

def main():
    if st.session_state.user is None:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            login_page()
        with tab2:
            signup_page()
    else:
        main_page()

if __name__ == "__main__":
    main() 