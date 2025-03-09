from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default='patient')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient_record = relationship("PatientRecord", back_populates="user", uselist=False)
    diagnoses_reviewed = relationship("Diagnosis", back_populates="reviewed_by_user")

class PatientRecord(Base):
    __tablename__ = "patient_records"

    record_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    medical_history = Column(Text)
    allergies = Column(Text)
    current_medications = Column(Text)
    family_history = Column(Text)
    blood_type = Column(String(5))
    height = Column(Float)
    weight = Column(Float)
    emergency_contact = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="patient_record")
    medical_parameters = relationship("MedicalParameter", back_populates="patient_record")
    diagnoses = relationship("Diagnosis", back_populates="patient_record")

class MedicalParameter(Base):
    __tablename__ = "medical_parameters"

    parameter_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey('patient_records.record_id', ondelete='CASCADE'))
    glucose_level = Column(Float)
    blood_pressure = Column(String(20))
    skin_thickness = Column(Float)
    insulin_level = Column(Float)
    bmi = Column(Float)
    diabetes_pedigree_function = Column(Float)
    age = Column(Integer)
    measurement_date = Column(DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        CheckConstraint('glucose_level > 0', name='chk_glucose_level'),
        CheckConstraint('bmi > 0', name='chk_bmi'),
        CheckConstraint('age > 0', name='chk_age'),
    )

    # Relationships
    patient_record = relationship("PatientRecord", back_populates="medical_parameters")

class Disease(Base):
    __tablename__ = "diseases"

    disease_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    common_symptoms = Column(Text)  # Store as JSON string
    risk_factors = Column(Text)     # Store as JSON string
    icd_10_code = Column(String(10))
    severity_level = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symptoms = relationship("Symptom", secondary="disease_symptoms", back_populates="diseases")
    diagnoses = relationship("Diagnosis", back_populates="disease")

class Symptom(Base):
    __tablename__ = "symptoms"

    symptom_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    severity_level = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    diseases = relationship("Disease", secondary="disease_symptoms", back_populates="symptoms")

class DiseaseSymptom(Base):
    __tablename__ = "disease_symptoms"

    disease_id = Column(Integer, ForeignKey('diseases.disease_id', ondelete='CASCADE'), primary_key=True)
    symptom_id = Column(Integer, ForeignKey('symptoms.symptom_id', ondelete='CASCADE'), primary_key=True)
    relevance_score = Column(Float)

    __table_args__ = (
        CheckConstraint('relevance_score BETWEEN 0 AND 1', name='chk_relevance_score'),
    )

class Diagnosis(Base):
    __tablename__ = "diagnoses"

    diagnosis_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey('patient_records.record_id', ondelete='CASCADE'))
    disease_id = Column(Integer, ForeignKey('diseases.disease_id'))
    confidence_score = Column(Float)
    diagnosis_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    model_version = Column(String(50))
    status = Column(String(20), default='pending')
    reviewed_by = Column(Integer, ForeignKey('users.user_id'))

    __table_args__ = (
        CheckConstraint('confidence_score BETWEEN 0 AND 100', name='chk_confidence_score'),
    )

    # Relationships
    patient_record = relationship("PatientRecord", back_populates="diagnoses")
    disease = relationship("Disease", back_populates="diagnoses")
    reviewed_by_user = relationship("User", back_populates="diagnoses_reviewed")

class ModelPerformance(Base):
    __tablename__ = "model_performance"

    performance_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50))
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_date = Column(DateTime, default=datetime.utcnow)
    dataset_version = Column(String(50))
    parameters = Column(Text)  # Store as JSON string

    __table_args__ = (
        CheckConstraint('accuracy BETWEEN 0 AND 1', name='chk_accuracy'),
        CheckConstraint('precision BETWEEN 0 AND 1', name='chk_precision'),
        CheckConstraint('recall BETWEEN 0 AND 1', name='chk_recall'),
        CheckConstraint('f1_score BETWEEN 0 AND 1', name='chk_f1_score'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    action_type = Column(String(50), nullable=False)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer)
    old_values = Column(Text)  # Store as JSON string
    new_values = Column(Text)  # Store as JSON string
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow) 