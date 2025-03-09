import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.database.database import engine, Base
from src.database.models import (
    User, PatientRecord, MedicalParameter, Disease,
    Symptom, DiseaseSymptom, Diagnosis, ModelPerformance,
    AuditLog
)

def init_database():
    """Initialize the database by creating all tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_database() 