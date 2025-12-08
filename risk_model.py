from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier

class RiskModel:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.classifier = DecisionTreeClassifier(max_depth=6, criterion='entropy')
        self.is_trained = False

    def train_mock_model(self):
        """
        Trains model based on Dhaka Logic:
        - 0: SAFE (Traffic jam, smooth riding, proactive behavior)
        - 1: MODERATE (Occasional hazards, mild swerves)
        - 2: CRITICAL (Reactive panic, pinch points, tailgating, distraction)
        """
        descriptions = [
            # --- SAFE (0) --- Smooth riding with objects around is OK in Dhaka
            "STABLE_LANE",
            "traffic_jam_safe stable_control",
            "tight_filtering rickshaw_proximity",
            "stable_control safe_gap",
            "STABLE_LANE smooth_riding",
            "traffic_jam_safe heavy_vehicle_conflict",
            "cng_proximity stable_control",
            "rickshaw_proximity traffic_jam_safe",
            "SPEED_BREAKER_IMPACT traffic_jam_safe",
            "heavy_vehicle_conflict STABLE_LANE",
            "cng_proximity STABLE_LANE",
            
            # --- MODERATE (1) ---
            "heavy_vehicle_conflict moderate",
            "rickshaw_proximity cng_proximity",
            "reactive_swerve traffic_jam_safe",
            "SPEED_BREAKER_IMPACT reactive_swerve",
            "tight_filtering reactive_swerve",
            "rickshaw_proximity reactive_swerve",
            
            # --- CRITICAL (2) ---
            "reactive_swerve tailgating_critical",
            "critical_pinch_point heavy_vehicle_conflict",
            "distracted_riding reactive_swerve",
            "tailgating_critical",
            "visibility_blindness reactive_swerve",
            "critical_pinch_point",
            # Add aggressive pinch entry examples
            "critical_pinch_point AGGRESSIVE_PINCH_ENTRY",
            "AGGRESSIVE_PINCH_ENTRY heavy_vehicle_conflict",
            "AGGRESSIVE_PINCH_ENTRY reactive_swerve",
            "critical_pinch_point AGGRESSIVE_PINCH_ENTRY cng_proximity",
            "AGGRESSIVE_PINCH_ENTRY",
            
            # --- NEW DETECTOR TOKENS (CRITICAL) ---
            "CRITICAL_LEGUNA_STOP",
            "WRONG_WAY_HAZARD",
            "ACTIVE_CROSSING_RISK",
            "BLIND_SPOT_LOITERING",
            "RED_LIGHT_VIOLATION",
            "AGGRESSIVE_GAP_SHOOTING",
            "BUS_BLOCKING_LANE",
            "AGGRESSIVE_WEAVING",
            "SLALOM_AGGRESSIVE"
        ]
        
        # labels: 11 SAFE (0), 6 MODERATE (1), remaining CRITICAL (2)
        labels = [0]*11 + [1]*6 + [2]*(len(descriptions) - 17)

        X_train = self.vectorizer.fit_transform(descriptions)
        self.classifier.fit(X_train, labels)
        self.is_trained = True
        print("Dhaka Risk Model trained.")

    def predict_risk(self, text_descriptions):
        if not self.is_trained: 
            raise Exception("Model not trained. Call train_mock_model() first.")
        if not text_descriptions:
            raise ValueError("Empty descriptions list provided.")
        X_new = self.vectorizer.transform(text_descriptions)
        return self.classifier.predict(X_new)

    def interpret_risk(self, risk_level):
        mapping = {0: "SAFE", 1: "CAUTION", 2: "DANGER"}
        return mapping.get(risk_level, "UNKNOWN")