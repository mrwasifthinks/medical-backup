from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from config.settings import MODEL_PATH, DEFAULT_MODEL
from src.database.models import (
    Diagnosis, Disease, PatientRecord, MedicalParameter,
    ModelPerformance
)
from src.database.schemas import (
    DiagnosisCreate, MedicalParameterCreate
)
from src.ml_models.random_forest import RandomForestModel

class DiagnosisService:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self) -> RandomForestModel:
        """Load the ML model."""
        model = RandomForestModel()
        model_path = MODEL_PATH / f"{DEFAULT_MODEL}.joblib"
        if model_path.exists():
            model.load_model(str(model_path))
        return model

    def create_medical_parameters(
        self, db: Session, params: Dict[str, Any], record_id: int
    ) -> MedicalParameter:
        """Create medical parameters record."""
        param_data = MedicalParameterCreate(
            record_id=record_id,
            glucose_level=params.get('glucose_level'),
            blood_pressure=params.get('blood_pressure'),
            skin_thickness=params.get('skin_thickness'),
            insulin_level=params.get('insulin_level'),
            bmi=params.get('bmi'),
            diabetes_pedigree_function=params.get('diabetes_pedigree_function'),
            age=params.get('age')
        )
        
        db_params = MedicalParameter(**param_data.dict())
        db.add(db_params)
        db.commit()
        db.refresh(db_params)
        return db_params

    def create_diagnosis(
        self, db: Session, 
        disease_id: int,
        record_id: int,
        confidence_score: float,
        model_version: str,
        notes: Optional[str] = None
    ) -> Diagnosis:
        """Create a diagnosis record."""
        diagnosis_data = DiagnosisCreate(
            disease_id=disease_id,
            record_id=record_id,
            confidence_score=confidence_score,
            model_version=model_version,
            notes=notes
        )
        
        db_diagnosis = Diagnosis(**diagnosis_data.dict())
        db.add(db_diagnosis)
        db.commit()
        db.refresh(db_diagnosis)
        return db_diagnosis

    def get_diagnosis_by_id(self, db: Session, diagnosis_id: int) -> Optional[Diagnosis]:
        """Get diagnosis by ID."""
        return db.query(Diagnosis).filter(Diagnosis.diagnosis_id == diagnosis_id).first()

    def get_patient_diagnoses(
        self, db: Session, record_id: int
    ) -> list[Diagnosis]:
        """Get all diagnoses for a patient."""
        return db.query(Diagnosis).filter(
            Diagnosis.record_id == record_id
        ).order_by(Diagnosis.diagnosis_date.desc()).all()

    def predict_disease(
        self, db: Session, params: Dict[str, Any], record_id: int
    ) -> Tuple[Disease, float]:
        """Make a disease prediction."""
        # Create medical parameters record
        self.create_medical_parameters(db, params, record_id)
        
        # Get prediction from model
        prediction, confidence = self.model.get_prediction_with_confidence(params)
        
        # Get disease from database
        disease = db.query(Disease).filter(Disease.disease_id == prediction).first()
        
        # Create diagnosis record
        self.create_diagnosis(
            db=db,
            disease_id=disease.disease_id,
            record_id=record_id,
            confidence_score=confidence,
            model_version=DEFAULT_MODEL,
            notes=f"Automated diagnosis using {DEFAULT_MODEL}"
        )
        
        return disease, confidence

    def update_model_performance(
        self, db: Session, 
        metrics: Dict[str, float],
        parameters: Dict[str, Any]
    ) -> ModelPerformance:
        """Update model performance metrics."""
        performance = ModelPerformance(
            model_name=DEFAULT_MODEL,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            dataset_version=datetime.utcnow().strftime("%Y%m%d"),
            parameters=parameters
        )
        db.add(performance)
        db.commit()
        db.refresh(performance)
        return performance 