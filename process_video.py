# process_video.py
import os
from video_processor import VideoProcessor
from text_generator import TextGenerator
from risk_model import RiskModel
from recommendations import RecommendationEngine

def process_ride_video(video_path):
    """
    Process video and return all analysis results.
    Returns: dict with stats, verdict, recommendations, etc.
    """
    # Initialize components
    processor = VideoProcessor(video_path, window_size=10)
    text_gen = TextGenerator()
    risk_ai = RiskModel()
    rec_engine = RecommendationEngine()
    risk_ai.train_mock_model()
    
    # Process video
    raw_frame_data = processor.process_video()
    if not raw_frame_data:
        return None
    
    # Generate descriptions
    descriptions = [text_gen.generate_description(f) for f in raw_frame_data]
    if not descriptions:
        return None
    
    # Predict risks
    risk_predictions = risk_ai.predict_risk(descriptions)
    
    # Initialize stats
    stats = {
        'Reactive Swerves': 0,
        'Pinch Points': 0,
        'Distracted Riding': 0,
        'Heavy Vehicle Conflicts': 0,
        'Tailgating': 0,
        'Leguna Emergency Stops': 0,
        'Wrong-Way Vehicles': 0,
        'Jaywalker Crossings': 0,
        'Blind Spot Loitering': 0,
        'Red Light Violations': 0,
        'Gap Shooting': 0,
        'Speed Breaker Hits': 0,
        'Bus Blockades': 0,
        'Weaving Events': 0,
        'Slalom Maneuvers': 0,
        'Aggressive Pinch Entries': 0
    }
    
    critical_frames = 0
    safe_frames = 0
    total_samples = len(descriptions)
    critical_events = []
    
    # Analyze frames
    for i, (desc, risk) in enumerate(zip(descriptions, risk_predictions)):
        risk_label = risk_ai.interpret_risk(risk)
        frame_id = raw_frame_data[i]['frame_id']
        frame = raw_frame_data[i]
        
        if risk == 2:
            critical_frames += 1
            critical_events.append({
                'frame_id': frame_id,
                'risk_label': risk_label,
                'description': desc
            })
            
            # Track stats
            if "reactive_swerve" in desc: stats['Reactive Swerves'] += 1
            if "critical_pinch_point" in desc: stats['Pinch Points'] += 1
            if "distracted_riding" in desc: stats['Distracted Riding'] += 1
            if "heavy_vehicle_conflict" in desc: stats['Heavy Vehicle Conflicts'] += 1
            if "tailgating_critical" in desc: stats['Tailgating'] += 1
            if "CRITICAL_LEGUNA_STOP" in desc or frame.get('leguna_brake'):
                stats['Leguna Emergency Stops'] += 1
            if "WRONG_WAY_HAZARD" in desc or frame.get('wrong_way'):
                stats['Wrong-Way Vehicles'] += 1
            if "ACTIVE_CROSSING_RISK" in desc or frame.get('jaywalker') == "ACTIVE_CROSSING_RISK":
                stats['Jaywalker Crossings'] += 1
            if "BLIND_SPOT_LOITERING" in desc or frame.get('blind_spot_loitering'):
                stats['Blind Spot Loitering'] += 1
            if "RED_LIGHT_VIOLATION" in desc or frame.get('red_light_violation'):
                stats['Red Light Violations'] += 1
            if "AGGRESSIVE_GAP_SHOOTING" in desc or frame.get('gap_shooting'):
                stats['Gap Shooting'] += 1
            if "SPEED_BREAKER_IMPACT" in desc or frame.get('speed_breaker'):
                stats['Speed Breaker Hits'] += 1
            if "BUS_BLOCKING_LANE" in desc or frame.get('bus_blockade'):
                stats['Bus Blockades'] += 1
            w = frame.get('weaving')
            if "AGGRESSIVE_WEAVING" in desc or w == True or (isinstance(w, str) and w == "AGGRESSIVE_WEAVING"):
                stats['Weaving Events'] += 1
            if "SLALOM_AGGRESSIVE" in desc or frame.get('slalom_aggressive'):
                stats['Slalom Maneuvers'] += 1
            if "AGGRESSIVE_PINCH_ENTRY" in desc or frame.get('intentional_pinch_entry'):
                stats['Aggressive Pinch Entries'] += 1
        elif risk == 0:
            safe_frames += 1
    
    # Calculate verdict
    risk_percentage = (critical_frames / total_samples) * 100 if total_samples > 0 else 0
    swerve_ratio = stats['Reactive Swerves'] / max(critical_frames, 1)
    aggressive_pinch_count = stats.get('Aggressive Pinch Entries', 0)
    
    verdict = "SAFE"
    reason = "Ride demonstrates safe behavior with minimal critical risks."
    
    if stats['Distracted Riding'] > 0:
        verdict = "UNSAFE"
        reason = "Active phone distraction detected. Any phone use while riding is considered unsafe."
    elif aggressive_pinch_count > 2:
        verdict = "MODERATE RISK"
        reason = f"Multiple intentional pinch point entries detected ({aggressive_pinch_count} instances). This is aggressive riding behavior that increases collision risk."
    elif stats['Wrong-Way Vehicles'] > 5 or stats['Bus Blockades'] > 10:
        verdict = "UNSAFE"
        reason = f"High-severity hazards detected (wrong-way: {stats['Wrong-Way Vehicles']}, bus blockades: {stats['Bus Blockades']}). Immediate awareness training needed."
    elif stats['Reactive Swerves'] > 20 and swerve_ratio > 0.5:
        verdict = "UNSAFE"
        reason = f"Excessive reactive swerving ({stats['Reactive Swerves']} instances, {swerve_ratio*100:.0f}% of critical frames). Indicates poor hazard anticipation."
    elif aggressive_pinch_count > 0 and risk_percentage > 10:
        verdict = "MODERATE RISK"
        reason = f"Intentional aggressive pinch point entry detected ({aggressive_pinch_count} instances) combined with other risks ({risk_percentage:.1f}% of ride). This indicates aggressive riding behavior."
    elif risk_percentage > 25:
        verdict = "UNSAFE"
        reason = f"High frequency of critical risks ({risk_percentage:.1f}% of ride). Immediate correction needed."
    elif risk_percentage > 15:
        verdict = "MODERATE RISK"
        reason = f"Occasional risky behaviors detected ({risk_percentage:.1f}% of ride). Caution and practice advised."
    elif risk_percentage > 5:
        verdict = "CAUTION"
        reason = f"Minor hazards detected ({risk_percentage:.1f}% of ride). Stay vigilant."
    else:
        verdict = "SAFE"
        reason = "Excellent defensive riding. Minimal hazards detected."
    
    # Get recommendations
    recommendations = rec_engine.get_recommendations(
        verdict, stats, descriptions, raw_frame_data
    )
    
    # Determine rider style
    reactive_ratio = stats['Reactive Swerves'] / max(critical_frames, 1)
    has_heavy_traffic = stats['Heavy Vehicle Conflicts'] > 50
    
    if stats['Reactive Swerves'] > 30 and not has_heavy_traffic:
        rider_style = "REACTIVE (Over-Sensitive)"
        style_analysis = "Rider reacts to minor threats excessively, even in light traffic."
    elif has_heavy_traffic and stats['Reactive Swerves'] > 10:
        rider_style = "DEFENSIVE (Appropriate for Dhaka)"
        style_analysis = "Rider responds well to heavy traffic with quick reflexes."
    else:
        rider_style = "PROACTIVE (Safe)"
        style_analysis = "Rider maintains smooth lane discipline and anticipates hazards."
    
    return {
        'stats': stats,
        'verdict': verdict,
        'reason': reason,
        'risk_percentage': risk_percentage,
        'total_samples': total_samples,
        'critical_frames': critical_frames,
        'safe_frames': safe_frames,
        'recommendations': recommendations,
        'critical_events': critical_events,
        'rider_style': rider_style,
        'style_analysis': style_analysis
    }

