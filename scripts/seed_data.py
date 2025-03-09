import sys
import json
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.database.database import SessionLocal
from src.database.models import Disease, Symptom, DiseaseSymptom
from src.services.auth_service import create_user
from src.database.schemas import UserCreate

# Sample disease data
DISEASES = [
    {
        "name": "Type 2 Diabetes",
        "description": "A chronic condition that affects the way the body processes blood sugar (glucose).",
        "common_symptoms": json.dumps([
            "Increased thirst",
            "Frequent urination",
            "Increased hunger",
            "Unintended weight loss",
            "Fatigue",
            "Blurred vision"
        ]),
        "risk_factors": json.dumps([
            "Obesity",
            "Physical inactivity",
            "Age over 45",
            "Family history of diabetes",
            "High blood pressure"
        ]),
        "icd_10_code": "E11",
        "severity_level": "moderate"
    },
    {
        "name": "Hypertension",
        "description": "A condition in which the force of the blood against the artery walls is too high.",
        "common_symptoms": json.dumps([
            "Headaches",
            "Shortness of breath",
            "Nosebleeds",
            "Flushing",
            "Dizziness"
        ]),
        "risk_factors": json.dumps([
            "Age",
            "Family history",
            "Obesity",
            "High sodium diet",
            "Smoking"
        ]),
        "icd_10_code": "I10",
        "severity_level": "moderate"
    }
]

# Sample symptoms data
SYMPTOMS = [
    {
        "name": "Increased thirst",
        "description": "Feeling thirstier than usual",
        "category": "general",
        "severity_level": "mild"
    },
    {
        "name": "Frequent urination",
        "description": "Need to urinate more often than usual",
        "category": "urinary",
        "severity_level": "mild"
    },
    {
        "name": "Headaches",
        "description": "Pain in the head or neck region",
        "category": "neurological",
        "severity_level": "moderate"
    }
]

def create_admin_user(db):
    """Create an admin user."""
    try:
        admin_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="Admin123!",
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        create_user(db, admin_data)
        print("✅ Admin user created successfully")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

def seed_diseases(db):
    """Seed diseases data."""
    try:
        for disease_data in DISEASES:
            disease = Disease(**disease_data)
            db.add(disease)
        db.commit()
        print("✅ Diseases seeded successfully")
    except Exception as e:
        print(f"❌ Error seeding diseases: {e}")
        db.rollback()

def seed_symptoms(db):
    """Seed symptoms data."""
    try:
        for symptom_data in SYMPTOMS:
            symptom = Symptom(**symptom_data)
            db.add(symptom)
        db.commit()
        print("✅ Symptoms seeded successfully")
    except Exception as e:
        print(f"❌ Error seeding symptoms: {e}")
        db.rollback()

def create_disease_symptom_relationships(db):
    """Create relationships between diseases and symptoms."""
    try:
        # Get all diseases and symptoms
        diseases = db.query(Disease).all()
        symptoms = db.query(Symptom).all()
        
        # Create some sample relationships
        for disease in diseases:
            common_symptoms = json.loads(disease.common_symptoms)
            for symptom in symptoms:
                if symptom.name in common_symptoms:
                    relationship = DiseaseSymptom(
                        disease_id=disease.disease_id,
                        symptom_id=symptom.symptom_id,
                        relevance_score=0.8
                    )
                    db.add(relationship)
        
        db.commit()
        print("✅ Disease-Symptom relationships created successfully")
    except Exception as e:
        print(f"❌ Error creating relationships: {e}")
        db.rollback()

def main():
    """Main function to seed the database."""
    print("🌱 Starting database seeding...")
    
    db = SessionLocal()
    try:
        create_admin_user(db)
        seed_diseases(db)
        seed_symptoms(db)
        create_disease_symptom_relationships(db)
        print("✅ Database seeding completed successfully!")
    except Exception as e:
        print(f"❌ Error during database seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 