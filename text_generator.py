class TextGenerator:
    def __init__(self):
        pass

    def generate_description(self, data):
        tokens = []
        
        # Validate required keys exist
        if not isinstance(data, dict):
            return ""
        
        # 1. Speed Context (The "Dhaka Filter")
        # Traffic jams (stationary/slow) excuse close proximity
        speed = data.get('speed', 'stationary')
        is_jam = speed in ['stationary', 'slow']
        
        # 2. Behavioral Profile (Reactive vs Proactive)
        # High jerk means the rider swerved suddenly (Reactive)
        jerk = data.get('jerk', 0)
        if jerk > 1.0:  # Lowered from 1.5 to 1.0 for better detection
            tokens.append("reactive_swerve")
        elif jerk < 0.5 and speed == 'fast':
            tokens.append("stable_control")

        # 3. Space Management (Pinch Points)
        if data.get('pinch', False):
            # Only excuse pinch points if truly stationary (traffic jam)
            # Slow speed + pinch point = still risky if intentional
            if speed == 'stationary':
                tokens.append("tight_filtering") # Normal in Dhaka traffic jam
            else:
                # Even in slow traffic, pinch points are risky if intentional
                if data.get('intentional_pinch_entry', False):
                    tokens.append("AGGRESSIVE_PINCH_ENTRY")
                tokens.append("critical_pinch_point") # High risk

        # 4. Object Hazards (Dhaka Specific)
        objects = data.get('objects', [])
        if isinstance(objects, list):
            if 'rickshaw' in objects: tokens.append("rickshaw_proximity")
            if 'cng' in objects: tokens.append("cng_proximity")
            if 'bus' in objects or 'truck' in objects: tokens.append("heavy_vehicle_conflict")

        # 5. Proximity Logic
        proximity = data.get('proximity', 0)
        if proximity > 0.4: # Very close
            if is_jam:
                tokens.append("traffic_jam_safe")
            else:
                tokens.append("tailgating_critical")
        
        # 6. Environmental
        if data.get('glare', False): tokens.append("visibility_blindness")
        #if data['phone']: tokens.append("distracted_riding")

        # 7. NEW: Advanced Hazard Detectors
        if data.get('leguna_brake'):
            tokens.append("CRITICAL_LEGUNA_STOP")
        if data.get('wrong_way'):
            tokens.append("WRONG_WAY_HAZARD")
        if data.get('jaywalker') == "ACTIVE_CROSSING_RISK":
            tokens.append("ACTIVE_CROSSING_RISK")
        if data.get('blind_spot_loitering'):
            tokens.append("BLIND_SPOT_LOITERING")
        if data.get('red_light_violation'):
            tokens.append("RED_LIGHT_VIOLATION")
        if data.get('gap_shooting'):
            tokens.append("AGGRESSIVE_GAP_SHOOTING")
        if data.get('speed_breaker'):
            tokens.append("SPEED_BREAKER_IMPACT")
        if data.get('bus_blockade'):
            tokens.append("BUS_BLOCKING_LANE")
        # weaving may be a boolean or a status string
        w = data.get('weaving')
        if w == True or (isinstance(w, str) and w == "AGGRESSIVE_WEAVING"):
            tokens.append("AGGRESSIVE_WEAVING")
        elif w == False or (isinstance(w, str) and w == "STABLE_LANE"):
            tokens.append("STABLE_LANE")
        if data.get('slalom_aggressive'):
            tokens.append("SLALOM_AGGRESSIVE")
        # Add intentional aggressive pinch entry detection
        if data.get('intentional_pinch_entry', False):
            tokens.append("AGGRESSIVE_PINCH_ENTRY")

        return " ".join(tokens)