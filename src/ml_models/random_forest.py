import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from .base_model import BaseDiagnosisModel
from typing import Dict, Any, Tuple

class RandomForestModel(BaseDiagnosisModel):
    def __init__(self):
        super().__init__()
        # Enhanced model parameters based on medical diagnosis requirements
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        
        # Initialize with training data
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize model with training data following the system architecture."""
        # Medical dataset (disease symptoms)
        X_train = np.array([
            # Healthy cases (Normal ranges)
            [85, 80, 20, 80, 22, 0.2, 35],   # Young adult, healthy
            [90, 85, 22, 90, 23, 0.3, 40],   # Middle-aged, healthy
            [95, 90, 25, 100, 24, 0.25, 45], # Middle-aged, healthy
            [92, 82, 21, 85, 21.5, 0.22, 38],# Adult, very healthy
            [88, 78, 19, 75, 20.5, 0.18, 32],# Young adult, athletic
            [93, 88, 23, 95, 23.5, 0.28, 42],# Middle-aged, active
            
            # Pre-diabetic cases (Borderline ranges)
            [120, 95, 28, 130, 27, 0.45, 50],  # Early pre-diabetes
            [125, 100, 30, 140, 28, 0.5, 55],  # Pre-diabetes with family history
            [130, 105, 32, 150, 29, 0.55, 60], # Pre-diabetes with hypertension
            [118, 98, 29, 135, 27.5, 0.48, 52],# Early pre-diabetes
            [128, 102, 31, 145, 28.5, 0.52, 57],# Pre-diabetes with obesity
            [122, 97, 28, 138, 27.8, 0.47, 51], # Pre-diabetes
            
            # Diabetic cases (Above threshold ranges)
            [140, 110, 35, 160, 31, 0.7, 65],  # Type 2 diabetes
            [150, 115, 38, 170, 32, 0.8, 70],  # Advanced diabetes
            [160, 120, 40, 180, 33, 0.9, 75],  # Severe diabetes
            [145, 112, 36, 165, 31.5, 0.75, 67],# Uncontrolled diabetes
            [155, 118, 39, 175, 32.5, 0.85, 72],# Long-term diabetes
            [142, 111, 35, 162, 31.2, 0.72, 66] # Moderate diabetes
        ])
        
        # Disease labels
        y_train = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2])
        
        # Split into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        # Train the model
        self.train(X_train, y_train)
        
        # Evaluate the model
        metrics = self.evaluate_model(X_val, y_val)
        print("Model Performance Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")

    def preprocess_blood_pressure(self, bp_str: str) -> float:
        """Convert blood pressure string to a single numeric value."""
        try:
            systolic, diastolic = map(float, bp_str.split('/'))
            # Use mean arterial pressure formula
            return (systolic + 2 * diastolic) / 3
        except (ValueError, AttributeError):
            return 0.0

    def preprocess_data(self, data: Dict[str, Any]) -> np.ndarray:
        """Preprocess input data with blood pressure handling."""
        processed_data = data.copy()
        if 'blood_pressure' in processed_data:
            processed_data['blood_pressure'] = self.preprocess_blood_pressure(processed_data['blood_pressure'])
        
        features = np.array([[
            float(processed_data.get(feature, 0)) for feature in self.feature_names
        ]])
        if self.scaler:
            features = self.scaler.transform(features)
        return features

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the Random Forest model following the preprocessing pipeline."""
        # Scale the features
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Train the model
        self.model.fit(X_scaled, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the Random Forest model."""
        return self.model.predict(X)

    def get_confidence_score(self, X: np.ndarray) -> float:
        """Get prediction probability as confidence score."""
        probabilities = self.model.predict_proba(X)
        confidence = float(np.max(probabilities[0]) * 100)  # Convert to percentage
        
        # Apply sigmoid scaling to boost mid-range confidences
        scaled_confidence = 100 / (1 + np.exp(-0.1 * (confidence - 50)))
        return scaled_confidence

    def get_feature_importance(self) -> dict:
        """Get feature importance scores for interpretability."""
        importance_scores = self.model.feature_importances_
        return dict(zip(self.feature_names, importance_scores)) 