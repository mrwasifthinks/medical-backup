from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any, Tuple, List
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler

class BaseDiagnosisModel(ABC):
    def __init__(self):
        self.model: BaseEstimator = None
        self.scaler: StandardScaler = None
        self.feature_names = [
            'glucose_level', 'blood_pressure', 'skin_thickness',
            'insulin_level', 'bmi', 'diabetes_pedigree_function', 'age'
        ]

    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean input data by handling missing values and outliers."""
        cleaned_data = {}
        for feature in self.feature_names:
            value = data.get(feature, 0)
            # Handle missing values
            if value is None or value == '':
                value = 0
            # Handle outliers using basic range checking
            if feature == 'glucose_level':
                value = np.clip(float(value), 0, 500)
            elif feature == 'blood_pressure':
                if isinstance(value, str) and '/' in value:
                    systolic, diastolic = map(float, value.split('/'))
                    systolic = np.clip(systolic, 70, 200)
                    diastolic = np.clip(diastolic, 40, 130)
                    value = f"{systolic}/{diastolic}"
            elif feature == 'skin_thickness':
                value = np.clip(float(value), 0, 100)
            elif feature == 'insulin_level':
                value = np.clip(float(value), 0, 1000)
            elif feature == 'bmi':
                value = np.clip(float(value), 0, 100)
            elif feature == 'diabetes_pedigree_function':
                value = np.clip(float(value), 0, 10)
            elif feature == 'age':
                value = np.clip(float(value), 0, 120)
            cleaned_data[feature] = value
        return cleaned_data

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data into the correct format for model input."""
        transformed_data = data.copy()
        
        # Handle blood pressure transformation
        if 'blood_pressure' in transformed_data:
            bp_str = transformed_data['blood_pressure']
            if isinstance(bp_str, str) and '/' in bp_str:
                systolic, diastolic = map(float, bp_str.split('/'))
                # Use mean arterial pressure formula
                transformed_data['blood_pressure'] = (systolic + 2 * diastolic) / 3
        
        return transformed_data

    def create_feature_vector(self, data: Dict[str, Any]) -> np.ndarray:
        """Create feature vector from transformed data."""
        features = np.array([[
            float(data.get(feature, 0)) for feature in self.feature_names
        ]])
        return features

    def preprocess_data(self, data: Dict[str, Any]) -> np.ndarray:
        """Complete preprocessing pipeline."""
        # 1. Clean the data
        cleaned_data = self.clean_data(data)
        
        # 2. Transform the data
        transformed_data = self.transform_data(cleaned_data)
        
        # 3. Create feature vector
        features = self.create_feature_vector(transformed_data)
        
        # 4. Scale features if scaler exists
        if self.scaler:
            features = self.scaler.transform(features)
        
        return features

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model with given data."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions for given data."""
        pass

    def get_prediction_with_confidence(self, data: Dict[str, Any]) -> Tuple[int, float]:
        """Get prediction and confidence score."""
        # Follow the system architecture flow
        features = self.preprocess_data(data)
        prediction = self.predict(features)
        confidence = self.get_confidence_score(features)
        return int(prediction[0]), float(confidence)

    @abstractmethod
    def get_confidence_score(self, X: np.ndarray) -> float:
        """Get confidence score for the prediction."""
        pass

    def save_model(self, path: str) -> None:
        """Save model to disk."""
        import joblib
        joblib.dump({'model': self.model, 'scaler': self.scaler}, path)

    def load_model(self, path: str) -> None:
        """Load model from disk."""
        import joblib
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']

    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance."""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        y_pred = self.predict(X_test)
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted')
        } 