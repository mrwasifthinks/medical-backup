from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr, confloat, conint

# Base Models
class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    role: Optional[str] = "patient"

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MedicalParameterBase(BaseModel):
    glucose_level: Optional[confloat(gt=0)] = None
    blood_pressure: Optional[str] = None
    skin_thickness: Optional[confloat(gt=0)] = None
    insulin_level: Optional[confloat(gt=0)] = None
    bmi: Optional[confloat(gt=0)] = None
    diabetes_pedigree_function: Optional[float] = None
    age: conint(gt=0)

class MedicalParameterCreate(MedicalParameterBase):
    record_id: int

class MedicalParameter(MedicalParameterBase):
    parameter_id: int
    measurement_date: datetime

    class Config:
        from_attributes = True

class PatientRecordBase(BaseModel):
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    family_history: Optional[str] = None
    blood_type: Optional[str] = None
    height: Optional[confloat(gt=0)] = None
    weight: Optional[confloat(gt=0)] = None
    emergency_contact: Optional[str] = None

class PatientRecordCreate(PatientRecordBase):
    user_id: int

class PatientRecord(PatientRecordBase):
    record_id: int
    created_at: datetime
    updated_at: datetime
    medical_parameters: List[MedicalParameter] = []

    class Config:
        from_attributes = True

class SymptomBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    severity_level: Optional[str] = None

class SymptomCreate(SymptomBase):
    pass

class Symptom(SymptomBase):
    symptom_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DiseaseBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    common_symptoms: List[str] = []
    risk_factors: List[str] = []
    icd_10_code: Optional[str] = None
    severity_level: Optional[str] = None

class DiseaseCreate(DiseaseBase):
    pass

class Disease(DiseaseBase):
    disease_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DiagnosisBase(BaseModel):
    disease_id: int
    confidence_score: confloat(ge=0, le=100)
    notes: Optional[str] = None
    model_version: str
    status: str = "pending"

class DiagnosisCreate(DiagnosisBase):
    record_id: int

class Diagnosis(DiagnosisBase):
    diagnosis_id: int
    diagnosis_date: datetime
    reviewed_by: Optional[int] = None
    disease: Disease

    class Config:
        from_attributes = True

class ModelPerformanceBase(BaseModel):
    model_name: str
    accuracy: confloat(ge=0, le=1)
    precision: confloat(ge=0, le=1)
    recall: confloat(ge=0, le=1)
    f1_score: confloat(ge=0, le=1)
    dataset_version: str
    parameters: dict

class ModelPerformanceCreate(ModelPerformanceBase):
    pass

class ModelPerformance(ModelPerformanceBase):
    performance_id: int
    training_date: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 